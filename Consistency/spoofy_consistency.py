import os
import time
import socket, multiprocessing, sys, threading, mysql.connector
import netifaces
from pathlib import Path
from dotenv import load_dotenv
from threading import Thread, Lock, Event
from queue import Queue
from collections import deque

PHP_PORT = 9000             # port used to receive MySQL commands from website
DEBUG = True                # indicates if debug messages should be printed
LOCALHOST = '127.0.0.1'     # IP addr of website
SERVER_SERVER_PORT = 10000  # port to send and receive messages between servers
PACKET_SIZE = 4096          # default size of packets to send and receive
TOKEN_MSG = 'Token~WR'      # token message inidicating local writes can be done

neighour = ""
snd_list = deque([])

dotenv_path = Path('../.env')
#==============================================================================
def debug_print(msg: str):
    '''
    Prints debug messages to console.

    param msg: message to print

    return N/A
    '''
    if(DEBUG):
        print(msg)
#==============================================================================

#==============================================================================
def run_cmd(php_listener: socket, out_queue: Queue, pool, acks: deque, \
            can_wr: Event, need_t: Event):

    '''
    This method receives MySql statements from the Spoofy website, executes 
    them, and adds them to the out queue.

    param php_listener: the socket used to communicate with the Spoofy website
    param out_queue: the queue of statements that must be sent to the other 
                     server replicas
    param pool: MySQL connection pool to pull a connection from
    param acks: list of ack messages from all other servers inidicating that
                the change to their databases was done locally
    param num_acks: the number of acks the server has received for a particular
                    action
    param can_wr: a thread Event inidicating that this server has the token
                  and can make changes to the database
    param need_t: a thread Event inidicating if this thread needs the token
                  so that it can make a database change

    return N/A
    '''
    global snd_list

    data = b''        # data containing MySQL query received from website

    # determine local IP addr
    hostname = socket.gethostname()
    # local_ip = socket.gethostbyname(hostname + '.local')
    if os.getenv('MACHINE') == 'MacOs':
        local_ip = netifaces.ifaddresses('en0')[netifaces.AF_INET][0]['addr']
        print(f"Local IP addr is: {local_ip}")
    else:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname + ".local")

    # receive data from client
    data = php_listener.recv(PACKET_SIZE)

    # format bytes received into a text string
    mysql_stmnt = data.decode()
    debug_print(f'Command received is:\n\"{mysql_stmnt}\"')

    # setup a connection to the local copy of the MySQL database
    spoofyDB = pool.get_connection()
    cursor = spoofyDB.cursor()

    # display if the server currently has the ability to change the databse
    # and if it needs to
    debug_print(f'Can \'{local_ip}\' write?: {can_wr}')
    debug_print(f'Does \'{local_ip}\' need the token?: {need_t}')

    # wait for token and once received execute the statement on the 
    # Spoofy database
    try:
        need_t.set()
        can_wr.wait()

        cursor.execute(mysql_stmnt)
        spoofyDB.commit()
        debug_print('Database update completed\n')
    except:
        debug_print('There was an error updating the database\n')
        spoofyDB.rollback()

    # forumulate the write message to send to all the other servers
    write_msg = 'WRITE~' + local_ip + '~' + mysql_stmnt

    # add the message to the out queue to send to the other servers
    out_queue.put(write_msg)

    # close connection to Spoofy database
    cursor.close()
    spoofyDB.close()

    ack_check = False
    health_ack_check = False
    health_check = False

    while not (ack_check or health_ack_check):
        ### NEW ###
        ack_check = acks_rcvd(acks, mysql_stmnt, len(snd_list), local_ip, health_check)
        # wait for ack from all other replicas that the write was performed
        # while not acks_rcvd(acks, mysql_stmnt, num_acks, local_ip):
        #     wait = 0

        if not ack_check:
            debug_print("I'm stuck in the ack_check loop")
            # deque([])
            # health_check(acks, mysql_stmnt, num_acks, local_ip)
            out_queue.put('HEALTH~')
            while not health_ack_check:
                health_check = True
                health_ack_check = acks_rcvd(acks, mysql_stmnt, len(snd_list), local_ip, health_check)
            health_check = False


    # add token to out queue and inidicate that no writing needs to be done
    # locally
    out_queue.put(TOKEN_MSG)
    can_wr.clear()
    need_t.clear()

    # close connection to the client
    php_listener.close()
#==============================================================================

#==============================================================================
def acks_rcvd(acks: deque, mysql_stmnt: str, num_acks: int, ip: str, health_check: bool):
    '''
    Keeps running until acks for a database change have been received from
    all other servers in the system.

    param acks: list of acks received from other servers
    param mysql_stmnt: the MySQL statement run on all servers
    param num_acks: the number of acks expected based on the number of 
                    other replicas in the system
    param ip: the ip address of this replica

    returns boolean: true if expected number of acks received, false otherwise
    '''

    acks_rcvd = 0 # number of acks received for a particular action
    health_acks_rcvd = 0
    debug_print(f'Checking if acks received for \'{ip}\'')

    # while the number of acks received doesn't equal the expected number of
    # acks, wait

    restart_timer = time.time()
    timeout = 3

    if health_check:
        while len(acks) != (num_acks * 2):
            wait = 0
            if restart_timer + timeout > time.time():
                break
    else:
        while len(acks) != num_acks:
            wait = 0
            if restart_timer + timeout > time.time():
                break
            
    debug_print(f'length of acks: {len(acks)} \t Number of acks: {num_acks}')
    debug_print(f'Am I in health check? {health_check}')
    # When the expected number of acks are received check them all and see if
    # they are acks, that they are meant to reply to this replica and that
    # the action they performed matches the expected action. If so increment
    # the number of acks received.

    for ack in acks:
        ack_msg = ack.split('~')
        if health_check:
            if ack_msg[0] == 'ACK' and ack_msg[1] == 'HEALTH':
                health_acks_rcvd += 1
        elif ack_msg[0] == 'ACK' and ack_msg[1] == 'HEALTH':
            acks_rcvd += 1
        elif ack_msg[0] == 'ACK' and ack_msg[1] == ip and  \
           ack_msg[2] == mysql_stmnt:
            acks_rcvd += 1

    # if the expected number of acks are received return True, else False
    if acks_rcvd == num_acks and not health_check:
        debug_print("Enter ack 1")
        # empty the acks list
        acks.clear()
        return True
    elif acks_rcvd == num_acks and health_acks_rcvd == num_acks and health_check:
        debug_print("Enter ack 2")
        # empty the acks list
        acks.clear()
        return True
    else :
        debug_print("Enter ack 3")
        return False

    return acks_rcvd
#==============================================================================

#==============================================================================
def snd_msgs(out_queue : Queue, init: str):

    '''
    If the outgoing message queue has mesasges in it this will send it to 
    every replica corresponding to the IP addresses provided to the program on
    startup. If the replica is starting for the first time and it's set as the
    primary it will initiate the passing of the token.

    param out_queue: outgoing messages queue
    param send_list: list of IP addresses to send query to
    param neighbour: the IP address of the next neighbour this replica should
                     send the token to
    param init: inidicates if this replica should initiate token passing
        
    return N/A
    '''
    global neighbour
    global snd_list

    # create a socket for sending messages
    msg_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # if this is the 'primary' replica starting passing the token by sending
    # it to this replica's neighbour
    if init == 'prim':
        msg_socket.connect((neighbour, SERVER_SERVER_PORT)) 
        msg_socket.send(TOKEN_MSG.encode())
        debug_print(f'Token forwarded to \'{neighbour}\'')
        msg_socket.close()

    # continue running this as long as the program runs
    while True:

        # while there are messages in the out queue do the following
        while not out_queue.empty():

            # pull the message at the front of the queue and prepare socket
            msg = out_queue.get()
            msg_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # if the message is an ack send it back to the replica that sent 
            # the database change

            if 'ACK~HEALTH' == msg:
                # send the message to every other server in the DS
                for ip in snd_list:
                    try:
                        msg_socket.connect((ip, SERVER_SERVER_PORT))
                        msg_socket.sendall(msg.encode())
                        debug_print(f'Health Check sent to {ip}:\n\"{msg}\"')
                    except ConnectionRefusedError:
                        debug_print(f'The server {ip} refused the connection on port {SERVER_SERVER_PORT}\n')
                        out_queue.put('LOST~' + ip)
                    except TimeoutError:
                        debug_print(f'Connection timeout on server {ip} with port {SERVER_SERVER_PORT}\n')
                        out_queue.put('LOST~' + ip)

                    # close connection to this particular server
                    msg_socket.close()

            elif 'ACK~' in msg:
                contents = msg.split('~')
                # msg_socket.connect((contents[1], SERVER_SERVER_PORT))
                # msg_socket.send(msg.encode())
                # msg_socket.close()
                try:
                    msg_socket.connect((contents[1], SERVER_SERVER_PORT))
                    msg_socket.sendall(msg.encode())
                except ConnectionRefusedError:
                    debug_print(f'The server {contents[1]} refused the connection on port {SERVER_SERVER_PORT}\n')
                    out_queue.put('LOST~' + contents[1])
                except TimeoutError:
                    debug_print(f'Connection timeout on server {contents[1]} with port {SERVER_SERVER_PORT}\n')
                    out_queue.put('LOST~' + contents[1])
                msg_socket.close()

            # if the message is the token pass it on to this replica's neighbour

            elif TOKEN_MSG in msg:
                try:
                    msg_socket.connect((neighbour, SERVER_SERVER_PORT)) 
                    msg_socket.sendall(msg.encode())
                except Exception as e:
                    msg_socket.close()
                    # unable to pass the token
                    notify_lost_neighbour = 'LOST~' + neighbour

                    # send_list.remove(neighbour)
                    # (neighbour, _) = process_ips(send_list)

                    # Here I want to notify everyone else in the send_list to remove
                    # msg_socket.connect((neighbour, SERVER_SERVER_PORT))
                    # msg_socket.send(notify_lost_neighbour.encode())

                    # msg_socket.send(msg.encode())
                    out_queue.put(notify_lost_neighbour)

                debug_print(f'Token forwarded to \'{neighbour}\'')
                msg_socket.close()

            # If the message is a health check
            elif 'HEALTH~' in msg:
                # send the message to every other server in the DS
                for ip in snd_list:
                    try:
                        msg_socket.connect((ip, SERVER_SERVER_PORT))
                        msg_socket.sendall(msg.encode())
                        debug_print(f'Health Check sent to {ip}:\n\"{msg}\"')
                    except ConnectionRefusedError:
                        debug_print(f'The server {ip} refused the connection on port {SERVER_SERVER_PORT}\n')
                        out_queue.put('LOST~' + ip)
                    except TimeoutError:
                        debug_print(f'Connection timeout on server {ip} with port {SERVER_SERVER_PORT}\n')
                        out_queue.put('LOST~' + ip)

                    # close connection to this particular server
                    msg_socket.close()

            # Notify of server going down
            elif 'LOST~' in msg:
                lost_ip = msg.split('~')
                for ip in snd_list:
                    try:
                        msg_socket.connect((ip, SERVER_SERVER_PORT))
                        msg_socket.send(msg.encode())
                        debug_print(f'Message sent to {ip}:\n\"{msg}\"')
                    except ConnectionRefusedError:
                        debug_print(f'The server {ip} refused the connection on port {SERVER_SERVER_PORT}\n')
                        out_queue.put('LOST~' + ip)
                    except TimeoutError:
                        debug_print(f'Connection timeout on server {ip} with port {SERVER_SERVER_PORT}\n')
                        out_queue.put('LOST~' + ip)

                    # close connection to this particular server
                    msg_socket.close()
                if lost_ip in snd_list:
                    snd_list.remove(lost_ip) # HRMMMM
                    process_ips(snd_list) # HRMMM

            # otherwise the message is a database statement that all the other
            # replicas must run, so send it to all other replicas

            else:
                # send the message to every other server in the DS
                for ip in snd_list:
                    try:
                        msg_socket.connect((ip, SERVER_SERVER_PORT))
                        msg_socket.send(msg.encode())
                        debug_print(f'Message sent to {ip}:\n\"{msg}\"')
                    except ConnectionRefusedError:
                        debug_print(f'The server {ip} refused the connection on port {SERVER_SERVER_PORT}\n')
                        out_queue.put('LOST~' + ip)
                    except TimeoutError:
                        debug_print(f'Connection timeout on server {ip} with port {SERVER_SERVER_PORT}\n')
                        out_queue.put('LOST~' + ip)

                    # close connection to this particular server
                    msg_socket.close()

            debug_print('Message sent\n')
#==============================================================================

#==============================================================================
def php_listener(out_queue: Queue, pool, acks: deque, num_acks: int, \
                 can_wr: Event, need_t: Event):

    '''
    Sets up a socket connection to listen for messages from Spoofy website

    param out_queue: queue to store received messages in so they can be sent to 
                     other servers
    param pool: collection pool of connections to the MySQL database
    param acks: list of acks received from other replicas
    param num_acks: the number of acks received from other replicas
    param can_wr: thread Event inidicating if this replica can make changes to
                  the database
    param need_t: thread Even inidicating if this replica wants to make changes
                  to the database

    return N/A
    '''

    # create the socket and extract the hostname & ip information from it
    php_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # start the socket
    php_listener.bind((LOCALHOST, PHP_PORT))
    php_listener.listen(5)

    while True:
        # keep listening for new messages from the Spoofy website and when 
        # received process the message
        (php_socket, _) = php_listener.accept()
        debug_print(f'Received command from Spoofy')

        # run the command received from Spoofy
        threading.Thread(target=run_cmd, \
                         args=(php_socket, out_queue, pool, acks, \
                         can_wr, need_t)).start()

#==============================================================================
def run_remote_cmds(in_queue: Queue, out_queue: Queue, pool):

    '''
    Checks for messages in the in queue. While it contains messages this method
    will remove them from the queue and run them on the local MySQL database.
    Once the command has been run on the database an ack will be created and
    put in the out queue.

    param in_queue: queue of messages received from other servers
    param out_queue: queue of messages to send out to other replicas
    param pool: pool of connections to MySQL server

    return N/A
    '''
    health_or_lost = False
    # while the in queue contains items do the following
    while True:
        while not in_queue.empty():

            # retrieve the oldest message in the in queue and split it apart
            # so you can grab the actual MySQL statement
            data_item = in_queue.get().split('~')

            debug_print(f'Commands for writing are: {data_item}')

            # create connection to local database
            db = pool.get_connection()
            cursor = db.cursor()

            if data_item[0] == "HEALTH":
                debug_print("Am going to add this ACK")
                ack = 'ACK~' + "HEALTH"
                health_or_lost = True
            elif data_item[2] == "LOST":
                ack = 'ACK~' + data_item[1] + '~LOST'
                health_or_lost = True
            else:
                # execute the command in the message on the database
                try:
                    cursor.execute(data_item[2])
                    db.commit()
                    debug_print("Database update complete\n")
                except:
                    debug_print("There was an error updating the database\n")
                    db.rollback()

            if not health_or_lost:
            # format ack message and add it to out queue
                ack = 'ACK~' + data_item[1] + '~' + data_item[2]  
              
            out_queue.put(ack)

            health_or_lost = False

            # close the connection to the database
            cursor.close()
            db.close()
#==============================================================================

#==============================================================================
def server_listener(in_queue: Queue, out_queue: Queue, acks: deque, \
                    can_wr: Event, need_t: Event):

    '''
    This method listens for messages from other replica servers.

    param in_queue: queue of messages received from other servers
    param out_queue: queue of messages to send to other replicas
    param acks: list of acks received from other servers
    param can_wr: thread Event inidcating if this replica can make changes to
                  the database
    param need_t: thread Event indicating if this replica wants to make 
                  changes to the database

    return N/A
    '''

    # create a socket to listen for messages from other servers
    server_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # ip = socket.gethostbyname(hostname + '.local')

    if os.getenv('MACHINE') == 'MacOs':
        ip = netifaces.ifaddresses('en0')[netifaces.AF_INET][0]['addr']
        print(f"Local IP addr is: {ip}")
    else:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname + ".local")

    debug_print(f"Local IP addr is: {ip}")

    # start listening for other servers
    server_listener.bind((ip, SERVER_SERVER_PORT))
    server_listener.listen(5)

    # keep accepting connections from other servers and processing the
    # messages received from them
    while True:
        (server_socket, addr) = server_listener.accept()
        debug_print(f'Received connection from {addr}:')

        threading.Thread(target=rcv_msg, args=(server_socket, in_queue, \
                         out_queue, acks, can_wr, need_t)).start()
#==============================================================================


#==============================================================================
def rcv_msg(conn, in_queue: Queue, out_queue: Queue, acks: deque, \
            can_wr: Event, need_t: Event):

    '''
    This method will receive messages from other replica servers and add those
    messages to the in queue or add them to the list of acks.

    param conn: socket connection to a server
    param in_queue: queue of messages received from other servers
    param out_queue: queue of messages to send to other replicas
    param acks: list of acks received from other replicas
    param can_wr: thread Event inidcating if this replica can make changes to
                  the database
    param need_t: thread Event indicating if this replica wants to make 
                  changes to the database

    return N/A
    '''
    global snd_list

    # receive a message from another replica
    rcvd_msg = conn.recv(PACKET_SIZE).decode()
    if rcvd_msg != TOKEN_MSG:
        debug_print(f'Message received is:\n\"{rcvd_msg}\"')

    # if the message is the token and this replica wants to make changes to the
    # database then set this replica's ability to do so to True

    if rcvd_msg == TOKEN_MSG and need_t.is_set():
        can_wr.set()

    # if the message is the token and this replica doesn't need to make changes
    # to the database add it to the out queue to be passed along

    elif rcvd_msg == TOKEN_MSG and not need_t.is_set():
        out_queue.put(rcvd_msg)

    elif 'LOST~' in rcvd_msg:
        ip_msg = rcvd_msg.split('~')
        if ip_msg[1] in snd_list:
            snd_list.remove(ip_msg[1]) # HRMMM
            process_ips(snd_list) # HRMM
        # todo() # I need to remove the ip address from the send list
        # acks.append('HEALTH~ACK')
        # pass # Legit do nothing here

    # if the message is an ack, add this ack to the list of acks

    elif 'ACK~' in rcvd_msg:
        acks.append(rcvd_msg)

    # otherwise the message is change to the database so add it to the in queue
    # until it can be processed

    else:
        in_queue.put(rcvd_msg)

    # close the connection for receiving messages
    conn.close()
#==============================================================================

#==============================================================================
def process_ips(ip_addrs: list):

    '''
    Creates a list of other replica IP addresses that messages must be sent to.
    Also determines who this replica's neighbour is, so that the token can be
    passed directly to that neighbour.

    param ip_addrs: list of replica IP addresses present in the DS

    return (neighbour, sorted_ips): tuple containing this replicas direct
                                    neighbour's ip and a list of all the other
                                    replicas in the DS
    '''
    global neighbour

    # determine local IP
    # hostname = socket.gethostname()
    # ip = socket.gethostbyname(hostname + '.local')

    if os.getenv('MACHINE') == 'MacOs':
        ip = netifaces.ifaddresses('en0')[netifaces.AF_INET][0]['addr']
        print(f"Local IP addr is: {ip}")
    else:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname + ".local") 

    # sort the list of replica IPs in ascending order
    sorted_ips = sorted(ip_addrs)

    # determine where this replica's IP is in the list of IPs
    own_index = sorted_ips.index(ip)

    # determine this replica's neighbour's IP address to send the token to
    if own_index == (len(sorted_ips) - 1):
        neighbour = sorted_ips[0]
    else:
        neighbour = sorted_ips[own_index + 1]

    # remove this replica's IP from the list, no need to send messages to itself
    sorted_ips.remove(ip)

    debug_print(f'Token neighbour is \'{neighbour}\'')
    debug_print(f'List of other replicas is {sorted_ips}')

    return (neighbour, sorted_ips)

#==============================================================================
def main():
    global neighbour
    global snd_list

    load_dotenv(dotenv_path=dotenv_path)

    out_queue = Queue()     # out queue of messages to send to other replicas
    in_queue = Queue()      # in queue of messages received from other replicas

    can_write = threading.Event()  # thread even indicating if this repllica can
                                   # make changes to the databas
    need_token = threading.Event() # thread event inidcating if this replica
                                   # wants to make changes to the database
    acks = deque([], maxlen=len(sys.argv[3:])) # contains acks that a write 
                                               # operation was performed
                                               # across all other replicas

    debug_print(f'Replication sender started')

    # determine the replica to send tokens to and all the replicas that writes
    # should be sent to

    (neighbour, snd_list) = process_ips(sys.argv[2:])


    # create connection pool for local MySQL database
    try:
        spoofyDB_config = {"database": os.getenv('DB_Name'),
                           "user":     os.getenv('DB_User'),
                           "password": os.getenv('DB_Pass'),
                           "host":     LOCALHOST}
        db_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="pool", \
                                                              **spoofyDB_config)
    except:
        debug_print("Could not create mysql connection.")
        debug_print("Consult README.md for more details.")
        exit(1)    

    # start the thread to receive MySQL commands from the database
    threading.Thread(target=php_listener, args=(out_queue, db_pool, acks, \
                     len(snd_list), can_write, need_token)).start()
    debug_print('Command receiver started')

    # start the thread to send messages to the other servers
    threading.Thread(target=snd_msgs, args=(out_queue, \
                     sys.argv[1])).start()
    debug_print('Send thread started')

    # start the thread to receive messages from other servers
    threading.Thread(target=server_listener, args=(in_queue, out_queue, \
                     acks, can_write, need_token)).start()

    # start the thread to run commands received from other servers
    threading.Thread(target=run_remote_cmds, args=(in_queue, out_queue, \
                     db_pool)).start()
    debug_print('Receive thread started')
#==============================================================================
def todo():
    raise NotImplementedError("This code is not yet implemented")

#==============================================================================

if __name__ == "__main__":
    main()    