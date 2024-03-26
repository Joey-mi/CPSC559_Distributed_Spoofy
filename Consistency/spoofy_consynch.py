# INSTRUCTIONS:

# - Run this code on every computer that will act as a replica
# - There will be one 'primary' replica and then the other replicas
# - All of the other replicas must be started before starting the primiary
#   replica
# - To run a non-primary replica write this on the command line:
#   'python spoofy_consynch.py no <list of all IPs in DS separate w/ spaces>''
#   For example, if you want to run the DS with three replicas w/ IPs of
#   10.0.0.131, 10.0.0.252, and 10.0.0.311 then you would input:
#   'python spoofy_consynch2.py no 10.0.0.131 10.0.0.252 10.0.0.311'
#   It doesn't matter what order you enter the IPs in.
# - Once the other replicas are running you can run the 'primary' replica.
#   You can start the primary with the same list of IPs but the first 
#   argument will be different. It will be:
#   'python spoofy_consynch.py prim 10.0.0.131 10.0.0.252 10.0.0.311'

import socket, multiprocessing, sys, threading, mysql.connector, time, os
import netifaces
from threading import Thread, Lock, Event
from queue import Queue
from collections import deque
from dotenv import load_dotenv
from pathlib import Path

PHP_PORT = 9000                # port used to receive MySQL commands from 
                               # website
DEBUG = True                   # indicates if debug messages should be printed
LOCALHOST = '127.0.0.1'        # IP addr of website
SERVER_SERVER_PORT = 10000     # port to send and receive messages between 
                               # servers
CHECK_PORT = 11000             # port used to communicate with other servers
                               # to determine which ones have crashed
PACKET_SIZE = 4096             # default size of packets to send and receive
TOKEN_MSG = 'Token~WR'         # token message inidicating local writes can be 
                               # done
TIMEOUT = 10                   # Time to wait to receive a token or ack. This 
                               # value can be altered to give more time.
SND_LIST = deque([])           # list of the other replica's IPs
SUCCESSOR = ''                 # the IP of the replica directly ahead of this
                               # one in the token passing ring
PREDECESSOR = ''               # the IP of the replica directly behind this one
                               # in the token passing ring
NUM_ACKS = 0                   # number of acks to expect from the other replicas
LOCAL_IP=''                    # local IP address of this replica
DOTENV_PATH = Path('../.env')  # path to .eve file

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
def process_ips(ip_addrs: list, to_remove: str, can_wr: Event):

    '''
    Creates a list of other replica IP addresses that messages must be sent to.
    Also determines who this replica's successor is, so that the token can be
    passed directly to that successor.

    param ip_addrs: list of replica IP addresses present in the DS
    param to_remove: the IP address to remove from the send list
    param can_wr: thread Event inidcating if this replica can make changes to
                  the database

    returns N/A
    '''

    global SUCCESSOR
    global PREDECESSOR
    global SND_LIST
    global NUM_ACKS

    # add the local ip to the provided list if it's not already there
    if LOCAL_IP not in ip_addrs:
        ip_addrs.append(LOCAL_IP)

    debug_print(f'All the IPs in the system are: {sorted(ip_addrs)}')

    # if a crashed replica's IP was provided remove it from the list
    if to_remove != '' and to_remove in ip_addrs:
        ip_addrs.remove(to_remove)
        debug_print(f'\'{to_remove}\' removed from SND_LIST')

    # sort the list of replica IPs in ascending order
    sorted_ips = sorted(ip_addrs)

    debug_print(f'{to_remove} dropped. All the IPs in the systems are now: {sorted_ips}')

    # determine where this replica's IP is in the list of IPs
    own_index = sorted_ips.index(LOCAL_IP)

    # Determine this replica's successor's IP address to send the token to.
    # SUCCESSOR is a global string, may need some massaging here to make 
    # it fully thread safe.
    if own_index == (len(sorted_ips) - 1):
        SUCCESSOR = sorted_ips[0]
    else:
        SUCCESSOR = sorted_ips[own_index + 1]

    # Determine this replica's predecessor's IP address. PREDECESSOR is a global
    # string, may need some massaging here to make it fully thread safe.
    if own_index == 0:
        PREDECESSOR = sorted_ips[-1]
    else:
        PREDECESSOR = sorted_ips[own_index - 1]

    # remove this replica's IP from the list, no need to send messages to itself
    sorted_ips.remove(LOCAL_IP)

    # Convert the sorted and formatted list to a deque. This is a global deque,
    # may need some massaging to make it fully thread safe here.
    SND_LIST = deque(sorted_ips)

    # Calculate the number of acks this replica should expect back. This is a 
    # global value, may need some massaging to make it fully thread safe here.
    NUM_ACKS = len(SND_LIST)

    # If this replica is the last one running in the DS set it so that it can
    # always make changes to the database
    if len(SND_LIST) == 0:
        can_wr.set()

    debug_print(f'Token predecessor is \'{PREDECESSOR}\'')
    debug_print(f'Token successor is \'{SUCCESSOR}\'')
    debug_print(f'List of other replicas is {SND_LIST}')
#==============================================================================

#==============================================================================
def php_listener(out_queue: Queue, pool, acks: deque, can_wr: Event, \
                 need_t: Event):

    '''
    Sets up a socket connection to listen for messages from Spoofy website

    param out_queue: queue to store received messages in so they can be sent to 
                     other servers
    param pool: collection pool of connections to the MySQL database
    param acks: list of acks received from other replicas
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
        (php_socket, addr) = php_listener.accept()
        debug_print(f'Received command from Spoofy')

        # run the command received from Spoofy
        threading.Thread(target=run_cmd, \
                         args=(php_socket, out_queue, pool, acks, can_wr, \
                         need_t), daemon=True).start()
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
    param can_wr: a thread Event inidicating that this server has the token
                  and can make changes to the database
    param need_t: a thread Event inidicating if this thread needs the token
                  so that it can make a database change

    return N/A
    '''

    data = b'' # data containing MySQL query received from website

    # receive data from client
    data = php_listener.recv(PACKET_SIZE)

    # format bytes received into a text string
    mysql_stmnt = data.decode()
    debug_print(f'Command received is:\n\"{mysql_stmnt}\"')

    # setup a connection to the local copy of the MySQL database
    spoofyDB = pool.get_connection()
    cursor = spoofyDB.cursor()

    # declare that this replica requires the token to write to the database
    need_t.set()

    # display if the server currently has the ability to change the databse
    # and if it needs to
    debug_print(f'Can \'{LOCAL_IP}\' write?: {can_wr.is_set()}')
    debug_print(f'Does \'{LOCAL_IP}\' need the token?: {need_t.is_set()}')

    # Wait until the token is received to proceed with database changes.
    # There's a chance that the token will not come and the wait will
    # timeout.
    token_recv = can_wr.wait(TIMEOUT)
    try_execution = True # indicates that execution should continue, either
                         # the token has been recieved and the database
                         # update will occur or the token was lost and a
                         # new one will be generated

    while try_execution:

        # if the token was received do the following
        if token_recv:
            try:
                cursor.execute(mysql_stmnt)
                spoofyDB.commit()
                debug_print('Database update completed\n')
            except mysql.connector.Error:
                debug_print('There was an error updating the database\n')
                spoofyDB.rollback()

            # formulate the write message to send to all the other servers
            write_msg = 'WRITE~' + LOCAL_IP + '~' + mysql_stmnt

            # add the write message to the out queue to send to the other servers
            out_queue.put(write_msg)

            # close connection to Spoofy database
            cursor.close()
            spoofyDB.close()

            # wait for ack from all other replicas that the write was performed
            acks_rcvd(out_queue, acks, mysql_stmnt, can_wr)

            # If there are still other servers in the DS then add token to out 
            # queue and inidicate that no writing needs to be done. Otherwise
            # if this is the only replica left then it can keep the ability
            # to write. But set it so this replica doesn't currently need the
            # token.
            if len(SND_LIST) != 0:
                out_queue.put(TOKEN_MSG)
                can_wr.clear()
            need_t.clear()

            # close connection to the client
            php_listener.close()

            # if a databse update occured then to loop can end
            try_execution = False

        # if there was a timeout and the token never arrived do the following
        else:
            # if the token never arrived then the predecessor crashed so log
            # its ip
            problem_ip = PREDECESSOR

            # remove the predecessor's ip from the list of ips and recalculate
            # this replica's predecessor and successor
            process_ips(list(SND_LIST), problem_ip, can_wr)

            # set up a message for the predecessor's ip to be dropped from all
            # other replica's send list
            out_queue.put('DROP~' + problem_ip)

            # now that the token is set to be sent again inidcate that this
            # replica has the token 
            can_wr.set()
            token_recv = True
#==============================================================================

#==============================================================================
def acks_rcvd(out_queue: Queue, acks: deque, mysql_stmnt: str, can_wr: Event):
    '''
    Keeps running until acks for a write operation have been received from
    all other servers in the system. The correctness of the acks are not
    considered here, just that the correct amount have been received.

    param out_queue: queue of messages to be sent to other replicas
    param acks: list of acks received from other servers
    param mysql_stmnt: the MySQL statement run on all servers
    param can_wr: event inidicating if this replica can perform a write op

    returns N/A
    '''

    drop_msgs = []
    if len(SND_LIST) != 0:
        debug_print(f'Checking if acks received for \'{LOCAL_IP}\'')
    else:
        debug_print('Only one replica remaining. No acks to receive.')

    # retrieve the current time in order to timeout if all acks are not
    # recieved
    start  = time.time()

    # while the number of acks received doesn't equal the expected number of
    # acks, wait
    while len(acks) != NUM_ACKS:

        # Calculate how long this loop has been running. If it has timed
        # out determine the replica that has not acked and proceed to
        # remove it from the list of ips
        current = time.time()
        if current - start > TIMEOUT:

            # convert the acks deque into a list of the acks
            ack_ips = ack_ips_to_list(acks)

            # determine the replicas acks have not been received from and remove
            # them from the send list and add them to a list of drop messages
            for ip_addr in SND_LIST:
                if ip_addr not in ack_ips:
                    process_ips(list(SND_LIST), ip_addr, can_wr)
                    drop_msgs.append('DROP~' + ip_addr)

            # add all the drop messages to the out queue
            for drop in drop_msgs:
                out_queue.put(drop)

            # the proper amount of acks have been received so this loop can end
            break

        # if the correct amount of acks have not been received and the timeout
        # has not occurred continue running this loop
        else:
            continue

    # empty the acks list
    acks.clear()
#==============================================================================

#==============================================================================
def ack_ips_to_list(acks: deque):
    '''
    Takes the deque of all the acks received and converts it into a list of
    just the IPs the acks were received from.

    param acks: all the acks received for a write operation

    return ack_ips: a list of the IPs acks were recieved from for a write 
                    operation
    '''

    ack_ips = []

    for ack in acks:
       ack_msg = ack.split('~')   
       ack_ips.append(ack_msg[2])  

    return ack_ips
#==============================================================================

#==============================================================================
def rcv_checks():
    '''
    Listens for connection attempts from other replicas. This is to make sure
    that this replica is still running. If this replica is not running then
    the replica attempting to connect will remove this replica from the send
    list.

    param N/A

    returns N/a
    '''

    # create a socket to listen for messages from other servers
    check_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # start listening for other servers
    check_listener.bind((LOCAL_IP, CHECK_PORT))
    check_listener.listen(5)

    # keep accepting connections from other servers to prove that this server
    # is still running
    while True:
        (check_socket, addr) = check_listener.accept()
        debug_print(f'Received check from from {addr}:')
#==============================================================================

#==============================================================================
def snd_msgs(out_queue: Queue, init: str, can_wr: Event):

    '''
    If the outgoing message queue has mesasges in it this will send it to 
    every replica corresponding to the IP addresses provided to the program on
    startup. If the replica is starting for the first time and it's set as the
    primary it will initiate the passing of the token.

    NOTE: LINES 345-375 ARE ATTEMPTING TO DEAL WITH THE PROBLEM OF A TOKEN
          BEING LOST IN BETWEEN SERVERS THAT AREN'T ATTEMPTING TO MAKE ANY
          WRITE OPERATION. NOT SURE IF THIS WILL WORK UNTIL FURTHER TESTING
          WITH > 2 COMPUTERS.

    param out_queue: outgoing messages queue
    param init: inidicates if this replica should initiate token passing
    param can_wr: threading event indicating if this replica can perform a
                  write operation on the database
        
    return N/A
    '''

    # if this is the 'primary' replica start passing the token by sending
    # it to this replica's successor
    if init == 'prim':
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as msg_socket:
            msg_socket.connect((SUCCESSOR, SERVER_SERVER_PORT)) 
            msg_socket.send(TOKEN_MSG.encode())
            debug_print(f'Token forwarded to \'{SUCCESSOR}\'')

    
    # note the start of the send operation to help test for timeouts
    start_time = time.time()

    # continue running this as long as the program runs
    while True:

        # note the current time to help test for timeouts
        current_time = time.time()

        # if a timeout has occurred and there are only two replicas in the DS
        # do the following
        if current_time - start_time > TIMEOUT and len(SND_LIST) > 1:

            # determine the IPs of all the crashed replicas
            crashed_replicas = detect_crashes()

            # remove all the failed replica IPs from the send list and recalculate
            # this replica's predecessor and neighbour
            for ip in crashed_replicas:
                process_ips(list(SND_LIST), ip, can_wr)

            # Queue up drop messages to be sent to all the other servers. This
            # can't be done in the above while loop because the send list is
            # constantly being changed so if these message were in the in queue
            # at that time there is a chance an error would occur where they
            # would be sent to crashed replicas. So these messages are added to 
            # the out queue now since the send list if finalized.
            for ip in crashed_replicas:
                out_queue.put('DROP~' + ip)

            # Put a token in the out queue as well so that token passing can
            # commence again. Not sure if this is the right thing to do,
            # ideally the token would be sent to the the first replica to
            # make a change after the token left this replica last time, but
            # unsure how to implement that w/o chanfing a lot of this and
            # adding timestamps to everything.
            out_queue.put(TOKEN_MSG)

    # while there are messages in the out queue do the following
        while not out_queue.empty():

            # pull the message at the front of the queue and prepare socket
            msg = out_queue.get()

            # if the message is an ack send it back to the replica that sent 
            # the database change
            if 'ACK~' in msg:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as msg_socket:
                    contents = msg.split('~')
                    msg_socket.connect((contents[1], SERVER_SERVER_PORT)) 
                    msg_socket.send(msg.encode())

            # if the message is the token pass it on to this replica's successor
            elif TOKEN_MSG in msg:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as msg_socket:
                    msg_socket.settimeout(TIMEOUT)
                    try:
                        msg_socket.connect((SUCCESSOR, SERVER_SERVER_PORT)) 
                        msg_socket.send(msg.encode())
                        debug_print(f'Token forwarded to \'{SUCCESSOR}\'')

                        # since the token was passed successfully start a timer
                        # now so that it can be checked if a token has been lost
                        start_time = time.time()
                    
                    # if the token was not passed successfully that means this
                    # replicas successor has crashed
                    except (TimeoutError, ConnectionRefusedError, \
                            ConnectionResetError):
                        debug_print(f'Unable to send token to successor \'{SUCCESSOR}\'')
                        
                        # set the ip of the replicas that has crashed
                        problem_ip = SUCCESSOR

                        # remove the successor's ip from the send list
                        process_ips(list(SND_LIST), problem_ip, can_wr)

                        # set up a drop message to be sent
                        out_queue.put('DROP~' + problem_ip)

            # otherwise the message is a database statement that all the other
            # replicas must run, so send it to all other replicas
            else:
                debug_print(f'The number of replicas to send to is: {len(SND_LIST)}')

                # send the message to every other server in the DS
                for ip in SND_LIST:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as \
                         msg_socket:
                        try:
                            msg_socket.connect((ip, SERVER_SERVER_PORT)) 
                            msg_socket.send(msg.encode())
                            debug_print(f'Message sent to {ip}:\n\"{msg}\"')
                        except (ConnectionRefusedError, ConnectionResetError, \
                                socket.gaierror):
                            debug_print(f'The server {ip} refused the connection on port {SERVER_SERVER_PORT}\n')

            debug_print('Message sent\n')
#==============================================================================

#==============================================================================
def detect_crashes():
    '''
    If this replica times out waiting for a token it will run this function
    to determine which of the replicas in the DS have crashed.

    param N/A

    returns crashed_replicas: list of IPs belonging to replicas that have
                              have crashed
    '''

    crashed_replicas = [] # list of replicas that have crashed

    # for every ip address in the current list of replica ips do the following
    for ip in SND_LIST:

        # Attempt to connect to the replica. If the connection is successful
        # then just continue, otherwise if an error is thrown note the ip
        # address that caused the connection to fail.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as check_socket:
            check_socket.settimeout(1)
            try:
                check_socket.connect((ip, CHECK_PORT))
            except (ConnectionRefusedError, ConnectionResetError, socket.gaierror,\
                    TimeoutError):
                crashed_replicas.append(ip)

    return crashed_replicas

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

    # start listening for other servers
    server_listener.bind((LOCAL_IP, SERVER_SERVER_PORT))
    server_listener.listen(5)

    # keep accepting connections from other servers and processing the
    # messages received from them
    while True:
        (server_socket, addr) = server_listener.accept()
        debug_print(f'Received connection from {addr}:')

        threading.Thread(target=rcv_msg, args=(server_socket, in_queue, \
                         out_queue, acks, can_wr, need_t), daemon=True).start()
#==============================================================================

#==============================================================================
def rcv_msg(conn: socket, in_queue: Queue, out_queue: Queue, acks: deque, \
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

    # receive a message from another replica
    rcvd_msg = conn.recv(PACKET_SIZE).decode()
    debug_print(f'Message received is:\n\"{rcvd_msg}\"')

    # if the message is the token and this replica wants to make changes to the
    # database then set this replica's ability to do so to True
    if rcvd_msg == TOKEN_MSG and need_t.is_set():
        can_wr.set()

    # if the message is the token and this replica doesn't need to make changes
    # to the database add it to the out queue to be passed along
    elif rcvd_msg == TOKEN_MSG and not need_t.is_set():
        out_queue.put(rcvd_msg)

    # if the message is an ack, add this ack to the list of acks
    elif 'ACK~' in rcvd_msg:
        acks.append(rcvd_msg)

    # If the message is a drop message then the server with the provided IP
    # must be removed from the send list and this replica's successor
    # and predecessor must be recalculated.
    # ***MUST TEST THIS WITH > 2 COMPUTERS***
    elif 'DROP~' in rcvd_msg:
        drop_msg = rcvd_msg.split('~')
        debug_print(f'Drop message received for {drop_msg[1]}')
        process_ips(list(SND_LIST), drop_msg[1], can_wr)

    # otherwise the message is A change to the database so add it to the in queue
    # until it can be processed
    else:
        in_queue.put(rcvd_msg)

    # close the connection for receiving messages
    conn.close()
#==============================================================================

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

    # while the in queue contains items do the following
    while True:

        while not in_queue.empty():

            # retrieve the oldest message in the in queue and split it apart
            # so you can grab the actual MySQL statement
            data_item = in_queue.get().split('~')

            # Sometimes when a replica crashes the others can receive an
            # empty write operatino. If this happens just ignore it.
            if data_item[0] != '':
                debug_print(f'Commands for writing are: {data_item}')

                # create connection to local database
                db = pool.get_connection()
                cursor = db.cursor()

                # execute the command in the message on the database
                try:
                    cursor.execute(data_item[2])
                    db.commit()
                    debug_print("Database update complete\n")
                except:
                    debug_print("There was an error updating the database\n")
                    db.rollback()

                # format ack message and add it to out queue
                ack = 'ACK~' + data_item[1] + '~' + LOCAL_IP + '~' + data_item[2]
                out_queue.put(ack)

                # close the connection to the database
                cursor.close()
                db.close()
#==============================================================================

#==============================================================================
def main():

    global LOCAL_IP                # local ip address of this replica
    out_queue = Queue()            # out queue of messages to send to other 
                                   # replicas
    in_queue = Queue()             # in queue of messages received from other 
                                   # replicas
    can_write = threading.Event()  # thread even indicating if this repllica 
                                   # can make changes to the databas
    need_token = threading.Event() # thread event inidcating if this replica
                                   # wants to make changes to the database
    acks = deque([])               # contains acks that a write operation was 
                                   # performed across all other replicas

    # allow the accessing of the .env file
    load_dotenv(dotenv_path=DOTENV_PATH)

    debug_print(f'Replication sender started')

    # determine local ip address
    if os.getenv('MACHINE') == 'MacOs':
        LOCAL_IP = netifaces.ifaddresses('en0')[netifaces.AF_INET][0]['addr']
        print(f"Local IP addr is: {LOCAL_IP}")
    else:
        hostname = socket.gethostname()
        LOCAL_IP = socket.gethostbyname(hostname + ".local") 

    # make an ordered list of all other replicase in the DS, determine this
    # replica's predecessor and successor and calculate the number of acks
    # this replica should receive
    process_ips(sys.argv[2:], '', can_write)

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
                     can_write, need_token), daemon=True).start()
    debug_print('Command receiver started')

    # start the thread to receive health inquiries from other replicas
    threading.Thread(target=rcv_checks, daemon=True).start()

    # start the thread to send messages to the other servers
    threading.Thread(target=snd_msgs, args=(out_queue, sys.argv[1],\
                     can_write), daemon=True).start()
    debug_print('Send thread started')

    # start the thread to receive messages from other servers
    threading.Thread(target=server_listener, args=(in_queue, out_queue, \
                     acks, can_write, need_token), daemon=True).start()

    # start the thread to run commands received from other servers
    threading.Thread(target=run_remote_cmds, args=(in_queue, out_queue, \
                     db_pool), daemon=True).start()
    debug_print('Receive thread started')

    # Run this loop so that the main thread will continue running. This is done
    # because Python 12.0 cannot run other threads if the main thread has
    # finished executing. This also allows for a keyboard interrupt to halt
    # execution of the entire program.
    try:
        while True:
            continue
    except KeyboardInterrupt:
        sys.exit(0)
#==============================================================================

if __name__ == "__main__":
    main()    