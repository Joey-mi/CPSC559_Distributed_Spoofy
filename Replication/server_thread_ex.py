import socket
import threading

# def server_program():

    # server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # ip = '127.0.0.1'
    # port = 5005 # port numbers must be greater than 1000
    # server_socket.bind((ip, port))
    # server_socket.listen(5) # argument indicates how many clients you want to be able to communicate w/ at the same time

    # while True:

    #     conn, addr = server_socket.accept()

    #     while True:
            
    #         data = conn.recv(1024).decode()
    #         print(f'Received from client {data}')

    #         if data == 'close':
    #             break
    #         else:
    #             message = input('->')
    #             conn.send(message.encode())

    #     conn.close()

def client_connection(client_socket, addr):

    while True:

        data = client_socket.recv(1024).decode()
        print(f'> Message received from client {addr}: {data}')

        if data == 'close':
            break
        else:
            message = input(f'> Reply to {addr}: ')

            # if message == 'shutdown':
            #     shutdown = 'The server has been shutdown. Please close connection.'
            #     client_socket.send(shutdown.encode())
            #     client_socket.close()
            #     break
            # else:
            client_socket.send(message.encode())

    client_socket.close()


def server_setup():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = '127.0.0.1'
    port = 5005 # port numbers must be greater than 1000

    print('> The server has started')
    print('> Waiting for clients...')

    server.bind((ip, port))
    server.listen(5)

    return server

if __name__ == "__main__":

    # server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # ip = '127.0.0.1'
    # port = 5005 # port numbers must be greater than 1000

    # print('> The server has started')
    # print('> Waiting for clients...')

    # server_socket.bind((ip, port))
    # server_socket.listen(5)

    server_socket = server_setup()

    while True:

        conn, addr = server_socket.accept()
        print(f'> Received connection from: {addr}')

        threading.Thread(target = client_connection, args = (conn, addr), daemon = True).start() 

        # message = input()

        # if message == 'shutdown':

        #     server_socket.close()
        #     break



        # new_thread = threading.Thread(client_connection(), (conn, addr))
        # new_thread.start()

    # server_socket.close()



    
    # server_program()