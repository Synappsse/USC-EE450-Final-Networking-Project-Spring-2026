import socket

HOST = '127.0.0.1' 
UDP_PORT = 25916 # 25000 + 916 (Last 3 digits of SID)

sock = socket.socket(type=socket.SOCK_DGRAM)
sock.bind((HOST, UDP_PORT))

#Boot message test
print(f"Hospital Server is up and running using UDP on port {UDP_PORT}.")

try:
    while True:
        data, sender = sock.recvfrom(1024)
        
#SImple Ctrl C exit
except KeyboardInterrupt:
    print("\nShutting down Hospital Server...")
finally: 
    sock.close()