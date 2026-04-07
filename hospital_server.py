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
tcpSock.listen(5)

# UDP setup to backend servers
udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpSock.bind((HOST, UDP_PORT))

print(f"Hospital Server is up and running using UDP on port {UDP_PORT}.")

try:
    # Keep looping to wait for client
    while True:

        clientConn, clientAddr = tcpSock.accept()
        clientData = clientConn.recv(1024)
        request_str = clientData.decode('utf-8')
       
       #Once the client sends something, split it up to help first authenticate or see what
       #Is going on with the client
        parts = request_str.split(",")
        cmd = parts[0]
        doctors, treatments = accessHospitalData() #Run the function to grab the latest data from hospital.txt

        #****************************************************************************
        # Purpose: Begin the authentication process once a client requests to login 
        #Once we confirm that the command is so authenticate, we can correctly 
        #Designate the different parts of the command as hashes
        #****************************************************************************
        if cmd == "AUTH" and len(parts) == 3:
            nameHash = parts[1]
            passHash = parts[2]
            suffixHash = nameHash[-5:]
            
            #First step after proper naming is to prepare the information and then send
            #it over to the authentication server.
            print(f"Hospital Server received an authentication request from a user with hash suffix {suffixHash}.")
            authReq = nameHash + "," + passHash
            udpSock.sendto(authReq.encode('utf-8'), (HOST, AUTH_PORT))
            print("Hospital Server has sent an authentication request to the Authentication Server.")
            
           #Then wait for a reply back from the server and catch, then decode whatever arrives
           #Allow the hospital server to confirm that an auth request was processed 
            authReplyBytes, authSender = udpSock.recvfrom(1024)
            authReply = authReplyBytes.decode('utf-8')
            print(f"Hospital server has received the response from the authentication server using UDP over port {UDP_PORT}.")
            
            
            if authReply == "SUCCESS":
                print(f"User with a hash suffix {suffixHash} has been granted access to the system. Determining the access of the user.")
                
                #Designate whether the client is a patient or a doctor based on their appearance in the hospital.txt file
                if nameHash in doctors:
                    print(f"User with hash suffix {suffixHash} will be granted doctor access.")
                    clientReply = "SUCCESS_DOC"
                
                else:
                    print(f"User with hash {suffixHash} will be granted patient access.")
                
                    clientReply = "SUCCESS_PAT"
            else:
                clientReply = "FAILED"
                
            # Lastly, we report back the client server with the result of their request
            clientConn.send(clientReply.encode('utf-8'))
            print(f"Hospital Server has sent the response from Authentication Server to the client using TCP over port {TCP_PORT}.")

    tcpSock.close()
    udpSock.close()