import socket
import requests

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(('', 5150)) #'' binds it to whatever ip this machine happens to have.
    s.listen()

    while True:
        client, addr = s.accept()
        with client:
            while True:
                data = client.recv(1024)
                if not data:
                    break # when we get 0 bytes then the sender is done, so we exit.
                
                r = requests.head('http://localhost:80/music/songs.php')
                if r.status_code<=399:
                    client.sendall(b'test') #put whatever string the proxy will be expecting here