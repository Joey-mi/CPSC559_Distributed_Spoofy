import socket

# Set the host and port for the server
host = '127.0.0.1'  # Change this to the desired IP address or use 'localhost'
port = 9000  # Change this to the desired port number

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_socket.bind((host, port))

# Listen for incoming connections
server_socket.listen()

print(f"Server listening on {host}:{port}")

while True:
    # Accept a connection from a client
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address}")

    # Receive and print data from the client
    data = client_socket.recv(1024)
    print(f"Received data: {data.decode('utf-8')}")

    # Close the client socket
    client_socket.close()