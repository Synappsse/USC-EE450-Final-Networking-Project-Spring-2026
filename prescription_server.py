import socket

#****************************************************************************
# Purpose: Define constants and bind the UDP socket.
#****************************************************************************
HOST = '127.0.0.1' 
UDP_PORT = 22916 #My SID

sock = socket.socket(type=socket.SOCK_DGRAM)
sock.bind((HOST, UDP_PORT))

#Boot message test
print(f"Prescription Server is up and running using UDP on port {UDP_PORT}.")

try:
    # Keep looping for data TEST
    while True:
        data, sender = sock.recvfrom(1024)
        

#Basic Ctrl C interupt
except KeyboardInterrupt:
    print("\nShutting down Prescription Server...")
finally: 
    sock.close()