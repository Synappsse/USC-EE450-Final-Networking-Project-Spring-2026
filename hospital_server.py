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
            
                            
            #Once we can approve the authentication request we need to move on to client roles
            #Designate whether the client is a patient or a doctor based on their appearance in the hospital.txt file
            if authReply == "SUCCESS":
                print(f"User with a hash suffix {suffixHash} has been granted access to the system. Determining the access of the user.")
                
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


        #****************************************************************************        
        # Purpose: Help the client lookup all available doctors at the moment. 
        #This will be done by taking the patients request and directly sending it
        #To the auth server, which will provide the list of available doctors.
        #****************************************************************************
        elif cmd == "LOOKUP" and len(parts) == 2:
            patHash = parts[1]
            suffixHash = patHash[-5:] 
            
            #Let server know we are awaiting lookup results
            print(f"Hospital Server received a lookup request from a user with a hash suffix {suffixHash} over port {TCP_PORT}.")
            
            udpMessage = "LOOKUP_ALL"
            udpSock.sendto(udpMessage.encode('utf-8'), (HOST, APT_PORT))
            print("Hospital Server sent the doctor lookup request to the Appointment server.")
            
            #Await reply from the apt server
            aptReplyBytes, aptSender = udpSock.recvfrom(1024)
            aptReply = aptReplyBytes.decode('utf-8')
           
           #Once the reply from the apt server is recieved, let the client know and send the data
            print(f"Hospital Server has received the response from Appointment Server using UDP over port {UDP_PORT}.")
            clientConn.send(aptReply.encode('utf-8'))
            print("Hospital Server has sent the doctor lookup to the client.")

        #****************************************************************************        
        # Purpose: Help the client lookup a specific doctor (Patients only).
        #This will be done by sending a req to the apt server and hashing
        #the clients command into multiple parts to look for only 1 doctor at a time.
        #****************************************************************************
        elif cmd == "LOOKUP_DOC" and len(parts) == 3:
            docName = parts[1]
            patHash = parts[2]
            suffixHash = patHash[-5:]
            
            print(f"Hospital Server has received a lookup request from a user with hash suffix {suffixHash} to lookup {docName} availability using TCP over port {TCP_PORT}.")
            
            # Forward the specific doctor lookup to the appointment server
            udpMessage = "LOOKUP_DOC," + docName
            udpSock.sendto(udpMessage.encode('utf-8'), (HOST, APT_PORT))
            print("Hospital Server sent the doctor lookup request to the Appointment server.")
            
            aptReplyBytes, aptSender = udpSock.recvfrom(1024)
            aptReply = aptReplyBytes.decode('utf-8')
            print(f"Hospital Server has received the response from Appointment Server using UDP over port {UDP_PORT}.")
            
            clientConn.send(aptReply.encode('utf-8'))
            print("The Hospital Server has sent the response to the client.")

          #****************************************************************************        
        # Purpose: Assist the client with scheduling an apt with a requested doctor.
        #This will be done by splitting their request into different variables that
        #The apt server will then confirm the apt or let the patient know of any issues.
        #****************************************************************************
        elif cmd == "SCHEDULE" and len(parts) == 5:
            docName = parts[1]
            timeBlock = parts[2]
            illness = parts[3]
            patHash = parts[4]
            suffixHash = patHash[-5:]
            print(f"Hospital Server has received a schedule request from a user with hash suffix: {suffixHash} to book an appointment using TCP over port {TCP_PORT}.")
            
            #Send over a formatted version of the client's request to the apt server
            udpMessage = "SCHEDULE," + docName + "," + timeBlock + "," + patHash + "," + illness
            udpSock.sendto(udpMessage.encode('utf-8'), (HOST, APT_PORT))

            print("Hospital Server has sent the schedule request to the appointment server.")
            
            aptReplyBytes, aptSender = udpSock.recvfrom(1024)
            aptReply = aptReplyBytes.decode('utf-8')
            print(f"Hospital Server has received the response from Appointment Server using UDP over {UDP_PORT}.")
            
            clientConn.send(aptReply.encode('utf-8'))
            print("The hospital server has sent the response to the client.")

          #****************************************************************************        
        # Purpose: Help the client cancel an appointment they already have/made.
        #Will do this by opening the patient request then pushing it to the apt server
        #****************************************************************************
        elif cmd == "CANCEL" and len(parts) == 2:
            patHash = parts[1]
            suffixHash = patHash[-5:]
            
            print(f"Hospital Server has received a cancel request from user with hash suffix: {suffixHash} to cancel their appointment using TCP over port {TCP_PORT}.")
            
            udpMessage = "CANCEL," + patHash
            udpSock.sendto(udpMessage.encode('utf-8'), (HOST, APT_PORT))
            print("The hospital server has sent the cancel request to the appointment server.")
            
            aptReplyBytes, aptSender = udpSock.recvfrom(1024)
            aptReply = aptReplyBytes.decode('utf-8')
            print(f"Hospital Server has received the response from Appointment Server using UDP over port {UDP_PORT}.")
            
            clientConn.send(aptReply.encode('utf-8'))
            print("The hospital server has sent the response to the client.")

         #****************************************************************************        
        # Purpose: Help the patient lookup a specific apt 
        #****************************************************************************
        elif cmd == "VIEW_PAT" and len(parts) == 2:
            patHash = parts[1]
            suffixHash = patHash[-5:]
            
            print(f"Hospital server has received a view appointment request from a user with hash suffix {suffixHash} to view their appointment details using TCP over port {TCP_PORT}.")
            
            udpMessage = "VIEW_PAT," + patHash
            udpSock.sendto(udpMessage.encode('utf-8'), (HOST, APT_PORT))
            print("Hospital Server has sent the view appointments request to the Appointment Server.")
            
            aptReplyBytes, aptSender = udpSock.recvfrom(1024)
            aptReply = aptReplyBytes.decode('utf-8')
            print(f"Hospital Server has received the response from the appointment server using UDP over port {UDP_PORT}.")
            
            clientConn.send(aptReply.encode('utf-8'))
            print("The hospital server has sent the response to the client.")
        
       
        clientConn.close()

# Basic Ctrl C interrupt 
except KeyboardInterrupt:
    print("\nShutting down Hospital Server...")
finally: 
    tcpSock.close()
    udpSock.close()
