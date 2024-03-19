import socket
import netifaces

def main():
    hostName = socket.gethostname()
    # hostName += ".local"
    ipAddr = socket.gethostbyname(hostName)

    print('Hostname is: {}'.format(hostName))
    print('IP Address is: {}'.format(ipAddr))

    # Get the IP address of the en0 interface
    en0_ip = netifaces.ifaddresses('en0').get(socket.AF_INET)
    if en0_ip:
        en0_ip = en0_ip[0]['addr']
        print(f"IP Address of en0 interface: {en0_ip}")

        # Perform a reverse DNS lookup to find the hostname
        try:
            hostname = socket.gethostbyaddr(en0_ip)[0]
            print(f"Hostname of en0 interface: {hostname}")
        except socket.herror:
            print("Hostname lookup failed.")
    else:
        print("No IP address found for en0 interface.")

if __name__ == "__main__":
    main()