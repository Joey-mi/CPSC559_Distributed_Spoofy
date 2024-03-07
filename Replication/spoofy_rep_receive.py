import mysql.connector, sys
import socket
import sys
from threading import Thread, Lock
from queue import Queue

PORT_NUM = 9001
LISTENFOR = 10000

def server_program():
    in_queue = Queue()

    lock = Lock()

    db = establish_connection()
    cursor = db.cursor()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Server socket open")
    ip = '127.0.0.1'
    port = LISTENFOR # port numbers must be greater than 1000
    server_socket.bind((ip, port))
    print("Server binded")
    server_socket.listen(5) # argument indicates how many clients you want to be able to communicate w/ at the same time
    print("Server listening")

    while True:

        conn, addr = server_socket.accept()
        acceptance = input('1')
        conn.send(acceptance.encode())

        u_thread = Thread(target=new_request_handler,args=(conn, db, cursor, lock, in_queue))

        u_thread.start()

        conn.close()

def establish_connection():
    try:
        db = mysql.connector.connect(
            host = "localhost",
            user = "spoofyUser",
            password = "testing",
            database = "SpoofyDB"
        )
        print("Connection to SpoofyDB established.")
    except:
        print("Could not create mysql connection.")
        print("Consult README.md for more details.")
        exit(1)
    return db

def atomic_database(db, cursor, lock, in_queue):
    data_item = in_queue.get(block=True)

    with lock:
        cursor.execute(data_item)
        db.commit()

def new_request_handler(con, db, cursor, lock, in_queue):
    recv_msg = ""
    while True:
        rtemp = con.recv(4096).decode
        print(f"Receieved from {con}")
        in_queue.put(rtemp, block=True)
        atomic_database(db, cursor, lock, in_queue)
        # if (rtemp == "close"):
        #     in_queue.put(recv_msg, block=True)
        #     recv_msg = ""
        #     atomic_database(db, cursor, lock, in_queue)
        # recv_msg += rtemp

if __name__ == "__main__":
    server_program()
        
