import socket, multiprocessing, sys, threading
from threading import Thread, Lock
from queue import Queue

PHP_PORT = 9000             # port used to receive MySQL commands from website
DEBUG = True                # indicates if debug messages should be printed
LOCALHOST = '127.0.0.1'     # IP addr of website
SERVER_SERVER_PORT = 10000  # port to send and receive messages between servers
PACKET_SIZE = 4096          # default size of packets to send and receive

#==============================================================================
# Prints debug messages to console.
#
# param msg: message to print
#
# return N/A
#==============================================================================
def debug_print(msg: str):
    
    if(DEBUG):
        print(msg)

#==============================================================================
# This method receives MySql statements from the Spoofy website, executes them,
# and adds them to the out queue.
#
# param php_listener: the socket used to communicate with the Spoofy website
# param out_queue: the queue of statements that must be sent to the other server
#                  replicas
# parap pool: MySQL connection pool to pull a connection from
#
# return N/A
#==============================================================================
def run_cmd(php_listener: socket, out_queue: Queue, pool):
    data = b'' # data containing MySQL query received from website

    # receive data from client
    data = php_listener.recv(PACKET_SIZE)

    # format bytes received into a text string
    mysql_stmnt = data.decode()
    debug_print(f'Command received is:\n\"{mysql_stmnt}\"')

    # setup a connection to the local copy of the MySQL database
    spoofyDB = pool.get_connection()
    cursor = spoofyDB.cursor()

    # execute the statement on the Spoofy database
    try:
        cursor.execute(mysql_stmnt)
        spoofyDB.commit()
        debug_print('Database update completed\n')
    except:
        debug_print('There was an error updating the database\n')
        spoofyDB.rollback()

    # add the message to the out queue to send to the other servers
    out_queue.put(mysql_stmnt)

    # close connection to Spoofy database
    cursor.close()
    spoofyDB.close()

    # close connection to the client
    php_listener.close()


#==============================================================================
# If the outgoing message queue has mesasges in it this will send it to every
# replica corresponding to the IP addresses provided to the program on
# startup.
#
# param out_queue: outgoing messages queue
# param send_queue: list of IP addresses to send query to
#
# return N/A
#==============================================================================
def snd_msgs(out_queue : Queue, send_queue):

    # continue running this as long as the program runs
    while True:

        # while there are messages in the out queue do the following
        while not out_queue.empty():

            # pull the message at the front of the queue
            msg = (out_queue.get()).encode()

            # send the message to every other server in the DS
            for ip in send_queue:
                try:
                    msg_socket = socket.socket(socket.AF_INET, \
                           socket.SOCK_STREAM)
                    msg_socket.connect((ip, SERVER_SERVER_PORT)) 
                    msg_socket.send(msg)
                    debug_print(f'Message sent to {ip}:\n\"{msg.decode()}\"')
                except ConnectionRefusedError:
                    debug_print(f'The server {ip} refused the connection on port {SERVER_SERVER_PORT}\n')

                # close connection to this particular server
                msg_socket.close()

                debug_print('Message sent\n')

#==============================================================================
# Sets up a socket connection to listen for messages from Spoofy website
#
# param out_queue: queue to store received messages in so they can be sent to 
#                  other servers
# param pool: collection pool of connections to the MySQL database
#
# return N/A
#==============================================================================
def php_listener(out_queue: Queue, pool):

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
                 args=(php_socket, out_queue, pool)).start()

#==============================================================================
# Checks for messages in the in queue. While it contains messages this method
# will remove them from the queue and run them on the local MySQL database.
#
# param in_queue: queue of messages received from other servers
# param pool: pool of connections to MySQL server
#
# return N/A
#==============================================================================
def run_remote_cmds(in_queue: Queue, pool):

    # while the in queue contains items do the following
    while True:
        while not in_queue.empty():

            # retrieve the oldest message in the in queue and create establish
            # a connection to the local MySQL database
            data_item = in_queue.get()
            db = pool.get_connection()
            cursor = db.cursor()

            # execute the command in the message on the database
            try:
                cursor.execute(data_item)
                db.commit()
                debug_print("Database update complete\n")
            except:
                debug_print("There was an error updating the database\n")
                db.rollback()

            # close the connection to the database
            cursor.close()
            db.close()

#==============================================================================
# This method listens for messages from other replica servers. 
#
# param in_queue: queue of messages received from other servers
#
# return N/A
#==============================================================================
def server_listener(in_queue: Queue):

    # create a socket to listen for messages from other servers
    server_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

        threading.Thread(target=rcv_msg, args=(server_socket, in_queue)).start()

#==============================================================================
# This method will receive messages from other replica servers and add those
# messages to the in queue.
#
# param conn: socket connection to a server
# param in_queue: queue of messages received from other servers
#
# return N/A
#==============================================================================
def rcv_msg(conn, in_queue: Queue):

    rcvd_msg = conn.recv(PACKET_SIZE).decode()
    debug_print(f'Message received is:\n\"{rcvd_msg}\"')

    in_queue.put(rcvd_msg)
    conn.close()

if __name__ == "__main__":

    out_queue = Queue() # out queue of messages to send to other replicas
    in_queue = Queue()  # in queue of messages received from other replicas

    debug_print(f'Replication sender started')

    # create connection pool for local MySQL database
    try:
        spoofyDB_config = {"database": "SpoofyDB",
                           "user":     "spoofyUser",
                           "password": "testing",
                           "host":     LOCALHOST}
        db_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="pool", \
                                                              **spoofyDB_config)
    except:
        debug_print("Could not create mysql connection.")
        debug_print("Consult README.md for more details.")
        # exit(1)    

    # start the thread to receive MySQL commands from the database
    threading.Thread(target=php_listener, args=(out_queue, db_pool)).start()
    debug_print('Command receiver started')

    # start the thread to send messages to the other servers
    threading.Thread(target=snd_msgs, args=(out_queue, sys.argv[1:])).start()
    debug_print('Send thread started')

    # start the thread to receive messages from other servers
    threading.Thread(target=server_listener, args=(in_queue)).start()

    # start the thread to run commands receive from other servers
    threading.Thread(target=run_remote_cmds, args=(in_queue, db_pool)).start()
    debug_print('Receive thread started')