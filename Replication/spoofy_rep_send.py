import socket
import sys
import threading
from threading import Thread
from queue import Queue
import mysql.connector
import multiprocessing

PHP_PORT_NUM = 9000
debug = True
localhost = '127.0.0.1'
send_port = 10000

#==============================================================================
# Prints debug messages to console.
#
# param msg: message to print
#
# return N/A
#==============================================================================
def debug_print(msg: str):
    
    if(debug):
        print(msg)

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

    # start the socket

    listener.bind((localhost, PHP_PORT_NUM))
    listener.listen(5)

    return listener

#==============================================================================
# This method receives MySql statements from the Spoofy website, executes them,
# and adds them to the out queue.
#
# param php_listener: the socket used to communicate with the Spoofy website
# param out_queue: the queue of statements that must be sent to the other server
#                  replicas
#
# return N/A
#==============================================================================
def retrieve_stmnts(php_listener: socket, out_queue: Queue):

    data = b''
    # chunks = []     # array of data received from Spoofy website
    # bytes_recvd = 0 # number of bytes received from Spoofy website

    # receive data from client

    data = php_listener.recv(4096)

    # Keep receiving data as it's sent. May implement more continuous listening
    # later if we decide we will actually receive song files.

    # while len(chunk) != 0:
    #     chunks.append(chunk)
    #     bytes_recvd = bytes_recvd + len(chunk)
    #     chunk = php_listener.recv(min(4096 - bytes_recvd, 4096))

    # format bytes received into a text string

    mysql_stmnt = data.decode()

    # setup a connection to the local copy of the MySQL database

    spoofyDB = mysql.connector.connect(user='spoofyUser', password='testing',
                                       host=localhost, database='SpoofyDB')
    mycursor = spoofyDB.cursor()

    debug_print(f'Message received is: {mysql_stmnt}')

    # execute the statement on the Spoofy database

    try:
        mycursor.execute(mysql_stmnt)
        spoofyDB.commit()
    except:
        spoofyDB.rollback()

    # add the message to the queue to send to the other servers

    out_queue.put(mysql_stmnt)

    # close connection to Spoofy database

    mycursor.close()
    spoofyDB.close()
    debug_print('Database update completed\n')

    # close connection to the client

    php_listener.close()


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

            # send the message to every other server in the DS

            for ip in send_queue:
                msg_socket = socket.socket(socket.AF_INET, \
                                           socket.SOCK_STREAM)
                try:
                    msg_socket.connect((ip, send_port)) 
                    msg_socket.send(msg)
                except ConnectionRefusedError:
                    print(f'The server {ip} refused the connection on port {send_port}\n')

                debug_print(f'Sent message:\n\"{msg.decode()}\"\nto {ip}')

                # close connection to this particular server

                msg_socket.close()

                debug_print('Message sent\n')

                ## may implement this send while loop if we decide to allow the
                ## sending of actual music files
                # total_sent = 0
                # while total_sent < len(msg):
                #     sent = msg_socket.send(msg[total_sent:])
                #     total_sent = total_sent + sent

if __name__ == "__main__":

    out_queue = Queue()         # out queue of messages to send to other replicas
    php_listener = listen_php() # socket listening for messages from Spoofy website

    debug_print(f'Replication sender started')
    
    send_stmnts = Thread(target=send_stmnts, args=(out_queue, sys.argv[1:]), \
                         daemon=True)
    send_stmnts.start()

    debug_print(f'Send thread started')

    while True:

        # keep listening for new messages from the Spoofy website and when 
        # received process the message

        (php_socket, addr) = php_listener.accept()

        debug_print(f'Received connection from: {addr}')

        threading.Thread(target=retrieve_stmnts, 
                         args=(php_socket, out_queue,)).start()