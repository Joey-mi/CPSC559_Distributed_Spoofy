import mysql.connector, sys
import socket
import sys
from threading import Thread, Lock
from queue import Queue

PORT_NUM = 9001
LISTENFOR = 10000
LOCALHOST = "127.0.0.1"

def server_program():

    in_queue = Queue()
    #lock = Lock()
    db_conns = establish_connection()
    #cursor = db.cursor()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Server socket open")
    #ip = '127.0.0.1'
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname + ".local")
    print(f"Local IP addr is: {ip}")

    port = LISTENFOR # port numbers must be greater than 1000
    server_socket.bind((ip, port))
    print("Server binded")
    server_socket.listen(5) # argument indicates how many clients you want to be able to communicate w/ at the same time
    print("Server listening")

    run_queries = Thread(target=atomic_database, args=(in_queue, db_conns))
    run_queries.start()

    while True:

        conn, addr = server_socket.accept()
        #acceptance = input('1')
        #conn.send(acceptance.encode())
        print(f'Received connection from {addr}:')

        u_thread = Thread(target=new_request_handler,args=(conn, in_queue))
        #u_thread = Thread(target=new_request_handler,args=(conn, db, cursor, lock, in_queue)
        u_thread.start()

        #conn.close()

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

#def atomic_database(db, cursor, lock, in_queue):
def atomic_database(in_queue, pool):

    while True:

        while not in_queue.empty():

            data_item = in_queue.get(block=True)
            db = pool.get_connection()
            cursor = db.cursor()

            try:
                #with lock:
                cursor.execute(data_item)
                db.commit()
                print("Database update complete\n")
            except:
                db.rollback()

            cursor.close()
            db.close()

#def new_request_handler(con, db, cursor, lock, in_queue):
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