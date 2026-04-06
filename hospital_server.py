import socket
import sys

#****************************************************************************
# Purpose: Opens hospital.txt to build a list of doctors and a dictionary 
# of treatments for illnesses. 
#****************************************************************************
def accessHospitalData():
    
    doctors = {}
    treatments = {}
    
    try:
        hospitalFile = open("hospital.txt", "r")
        docLookup = False
        treatmentLookup = False
        
        #Parses through the hospital.txt file, ignoring empty lines
        for line in hospitalFile:
            line = line.strip()
            if line == "":
                continue
                
            #Divide up each line based on their intended purpose
            #Mark the purpose with a flag in order to store the data 
            #properly in seperate vars.
            if line == "[Doctors]":
                docLookup = True
                treatmentLookup = False
                continue
            
            elif line == "[Treatments]":
                docLookup = False
                treatmentLookup = True
                continue
                
            parts = line.split()
            

             # Update the doctors dictionary with the name as the key and the hash as the value
            if docLookup and len(parts) == 2:
                doctors[parts[0]] = parts[1]

            #Update the illness dictionary with the illness as the key and the treatment as value
            elif treatmentLookup and len(parts) == 2:
                treatments[parts[0]] = parts[1]
                
        hospitalFile.close()
    except FileNotFoundError:
        print("Error: hospital.txt not there.")
        
    return doctors, treatments

#****************************************************************************
# Purpose: Define constants and bind the TCP and UDP sockets.     
#****************************************************************************
HOST = '127.0.0.1' 
UDP_PORT = 25916 # My SID, meant to talk to the backend servers
TCP_PORT = 26916 # My SID, meant to talk to the client


#Ports we set up and need to bind to for the backend
AUTH_PORT = 21916
PRES_PORT = 22916
APT_PORT = 23916

#TCP setup to Client
tcpSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpSock.bind((HOST, TCP_PORT))
tcpSock.listen(5) # Listen for incoming client connections

# UDP setup to backend servers
udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpSock.bind((HOST, UDP_PORT))

print(f"Hospital Server is up and running using UDP on port {UDP_PORT}.")

try:
    # Keep looping to wait for client
    while True:
        clientConn, clientAddr = tcpSock.accept()
        
        # Grab the data from the client once they send something
        clientData = clientConn.recv(1024)
        request_str = clientData.decode('utf-8')
       
        parts = request_str.split(",")
        cmd = parts[0]
        doctors, treatments = accessHospitalData()

        #****************************************************************************
        # Purpose: Begin the authentication process once a client requests to login 
        #****************************************************************************
        if cmd == "AUTH" and len(parts) == 3:
            nameHash = parts[1]
            passHash = parts[2]
            suffixHash = nameHash[-5:]
            
            print(f"Hospital Server received an authentication request from a user with hash suffix {suffixHash}.")
            
           
    tcpSock.close()
    udpSock.close()