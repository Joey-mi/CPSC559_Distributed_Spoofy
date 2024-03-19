import mysql.connector
import socket
import netifaces
import sys
import os
from dotenv import load_dotenv
from pathlib import Path
from threading import Thread
from queue import Queue

LISTENFOR = 10000
LOCALHOST = "127.0.0.1"
dotenv_path = Path('../.env')

def server_program():
    load_dotenv(dotenv_path=dotenv_path)

    in_queue = Queue()
    db_conns = establish_connection()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Server socket open")

    if os.getenv('MACHINE') == 'MacOs':
        ip = netifaces.ifaddresses('en0')[netifaces.AF_INET][0]['addr']
        print(f"Local IP addr is: {ip}")
    else:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname + ".local")
        print(f"Local IP addr is: {ip}")

    server_socket.bind((ip, LISTENFOR))
    print("Server binded")
    server_socket.listen(5) # argument indicates how many clients you want to be able to communicate w/ at the same time
    print("Server listening")

    run_queries = Thread(target=atomic_database, args=(in_queue, db_conns))
    run_queries.start()

    while True:

        conn, addr = server_socket.accept()
        print(f'Received connection from {addr}:')

        u_thread = Thread(target=new_request_handler,args=(conn, in_queue))
        u_thread.start()

def establish_connection():

    try:
        db_config = {"database": "SpoofyDB",
                     "user":     "spoofyUser",
                     "password": "testing",
                     "host":     "127.0.0.1"}
        db_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="pool", \

                                                              **db_config)
        print("SpoofyDB thread pool created.")

    except:
        print("Could not create mysql connection.")
        print("Consult README.md for more details.")
        exit(1)

    return db_pool

def atomic_database(in_queue, pool):

    while True:

        while not in_queue.empty():

            data_item = in_queue.get(block=True)
            db = pool.get_connection()
            cursor = db.cursor()

            try:
                cursor.execute(data_item)
                db.commit()
                print("Database update complete\n")
            except:
                print("There was an error updating the database\n")
                db.rollback()

            cursor.close()
            db.close()

def new_request_handler(con, in_queue):
    recv_msg = ""

    #while True:
    rtemp = con.recv(4096).decode()
    print(f"Message receieved is:\n\"{rtemp}\"")

    in_queue.put(rtemp, block=True)
    con.close()

        #atomic_database(db, cursor, lock, in_queue)
        # if (rtemp == "close"):
        #     in_queue.put(recv_msg, block=True)
        #     recv_msg = ""
        #     atomic_database(db, cursor, lock, in_queue)
        # recv_msg += rtemp

if __name__ == "__main__":
    server_program()