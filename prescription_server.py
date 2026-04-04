import socket
import sys

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

#****************************************************************************
#Purpose: Reads the prescriptions.txt file then stores it in a list for use 
#****************************************************************************

def createPresList():
    presList = []

    #open the prescriptions.txt file and input it into our list var, strip each line of whitespace and ignore blank lines
    try:
        txtFile = open("prescriptions.txt", "r")
        for line in txtFile:
            line = line.strip()
            if line is False:
                continue

            #Split the read file into 4 individual segments per none empty line
            parts = line.split()
            if len(parts) == 4:
                rx = {
                    "doctor": parts[0],
                    "patientHash": parts[1],
                    "treatment": parts[2],
                    "frequency": parts[3]
                }
                presList.append(rx) 

        txtFile.close() #close out the file once done and fully appended
    
    except FileNotFoundError:
        print("Error: prescriptions.txt not there.")
        
    return presList