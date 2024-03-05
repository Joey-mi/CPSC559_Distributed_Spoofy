import socket
import sys
from threading import Thread
from queue import Queue
import mysql.connector

PHP_PORT_NUM = 9000
debug = True

#==============================================================================
# Sets up a socket connection between to listen for messages from Spoofy
# website
#
# param N/A
#
# return N/A
#==============================================================================
def listen_php():

    # create the socket and extract the hostname & ip information from it

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hostname = socket.gethostname()
    ip_addr = socket.gethostbyname(hostname)

    # start the socket

    listener.bind((ip_addr, PHP_PORT_NUM))
    listener.listen(5)

    return listener

#==============================================================================
# This method receives mysql statements from the Spoofy website.
#
# param php_listener: the socket used to communicate with the Spoofy website
# param spoofyDB: connection the local instance of mysql Spoofy database so that
#                 the received statements can be run on it
# param out_queue: the queue of statements that must be sent to the other server
#                  replicas
#
# return N/A
#==============================================================================
def retrieve_stmnts(php_listener: socket, out_queue: Queue):

    chunks = []     # array of data received from Spoofy website
    bytes_recvd = 0 # number of bytes received from Spoofy website
    # the following is a connection the local copy of the Spoofy database
    spoofyDB = mysql.connector.connect(user='spoofyUser', password='testing',
                                       host=socket.getbyhostname(socket.gethostname()),
                                       database='SpoofyDB')

    # retrieve the mysql statement from PHP socket in Spoofy website

    chunk = php_listener.recv(4096)

    # while bytes_recvd <= 4096:
    while len(chunk) != 0:
        # chunk = php_listener.recv(min(4096 - bytes_recvd, 4096))
        chunks.append(chunk)
        bytes_recvd = bytes_recvd + len(chunk)
        chunk = php_listener.recv(min(4096 - bytes_recvd, 4096))

    # format bytes received into a text string

    mysql_stmnt = b''.join(chunks).decode()

    print(f'Message recieved is: {mysql_stmnt}')

    # execute the statement on the Spoofy database and add the statement into
    # the out queue

    spoofyDB.execute(mysql_stmnt)
    out_queue.put(mysql_stmnt)

    # close connection to Spoofy database

    spoofyDB.close()

#==============================================================================
# If the outgoing message queue has mesasges in it this will send it to every
# replica corresponding to the IP addresses provided to the program on
# execution.
#
# param out_queue: outgoing messages queue
#
# return N/A
#==============================================================================
def send_stmnts(out_queue : Queue, send_queue):

    # continue running this as long as the program runs

    while True:

        # while there are messages in the queue do the following

        while not out_queue.empty():

            # pull the message at the front of the queue

            msg = (out_queue.get()).encode()

            # send the message to every DS in the system

            # for ip in sys.argv[1:]:
            for ip in send_queue:
                msg_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                msg_socket.connect(ip, 10000) 
                total_sent = 0
                while total_sent < len(msg):
                    sent = msg_socket.send(msg[total_sent:])
                    total_sent = total_sent + sent
                msg_socket.close()

if __name__ == "__main__":

    out_queue = Queue()         # out queue of messages to send to other replicas
    php_listener = listen_php() # socket listening for messages from Spoofy website

    print(f'Replication sender started')
    
    send_stmnts = Thread(target=send_stmnts, args=(out_queue, sys.argv[1:]), daemon=True)
    send_stmnts.start()

    print(f'Send thread started')

    while True:

        # keep listening for new messages from the Spoofy website and when received
        # process the message

        (php_socket, addr) = php_listener.accept()

        print(f'Reveived connection from: {addr}')

        retrieve_stmnts = Thread(target=retrieve_stmnts, 
                                 args=(php_socket, out_queue), daemon=True)
        retrieve_stmnts.start()