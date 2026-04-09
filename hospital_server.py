import socket
import sys
import threading
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
                treatments[parts[0].lower()] = parts[1] 
                
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


#****************************************************************************
# Purpose: Handle individual client connections concurrently using threads.
# Resources Used: bgnet0_usl_c_1_2025.pdf - Chapter 42 Multithreading. I used
#this to teach me how to run multiple clients at the same time and have them
#speak to the hospital server
#****************************************************************************

def handle_client(clientConn):
    while True:
        clientData = clientConn.recv(1024)
        
        if not clientData:
            break
            
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
            
            #First step after proper naming is to prepare the information and then send
            #it over to the authentication server.
            print(f"Hospital Server received an authentication request from a user with hash suffix {suffixHash}.")
            authReq = nameHash + "," + passHash
            udpSock.sendto(authReq.encode('utf-8'), (HOST, AUTH_PORT))
            print("Hospital Server has sent an authentication request to the Authentication Server.")
            
            #Then wait for a reply back from the server and catch, then decode whatever arrives
            authReplyBytes, authSender = udpSock.recvfrom(1024)
            authReply = authReplyBytes.decode('utf-8')
            print(f"Hospital server has received the response from the authentication server using UDP over port {UDP_PORT}.")
                            
            #Once we can approve the authentication request we need to move on to client roles
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

        #**************************************************************************** # Purpose: Help the client lookup all available doctors at the moment. 
        #****************************************************************************
        elif cmd == "LOOKUP" and len(parts) == 2:
            patHash = parts[1]
            suffixHash = patHash[-5:] 
            
            print(f"Hospital Server received a lookup request from a user with a hash suffix {suffixHash} over port {TCP_PORT}.")
            
            udpMessage = "LOOKUP_ALL"
            udpSock.sendto(udpMessage.encode('utf-8'), (HOST, APT_PORT))
            print("Hospital Server sent the doctor lookup request to the Appointment server.")
            
            aptReplyBytes, aptSender = udpSock.recvfrom(1024)
            aptReply = aptReplyBytes.decode('utf-8')
           
            print(f"Hospital Server has received the response from Appointment Server using UDP over port {UDP_PORT}.")
            clientConn.send(aptReply.encode('utf-8'))
            print("Hospital Server has sent the doctor lookup to the client.")

        #**************************************************************************** # Purpose: Help the client lookup a specific doctor (Patients only).
        #****************************************************************************
        elif cmd == "LOOKUP_DOC" and len(parts) == 3:
            docName = parts[1]
            patHash = parts[2]
            suffixHash = patHash[-5:]
            
            print(f"Hospital Server has received a lookup request from a user with hash suffix {suffixHash} to lookup {docName} availability using TCP over port {TCP_PORT}.")
            
            udpMessage = "LOOKUP_DOC," + docName
            udpSock.sendto(udpMessage.encode('utf-8'), (HOST, APT_PORT))
            print("Hospital Server sent the doctor lookup request to the Appointment server.")
            
            aptReplyBytes, aptSender = udpSock.recvfrom(1024)
            aptReply = aptReplyBytes.decode('utf-8')
            print(f"Hospital Server has received the response from Appointment Server using UDP over port {UDP_PORT}.")
            
            clientConn.send(aptReply.encode('utf-8'))
            print("The Hospital Server has sent the response to the client.")

        #**************************************************************************** # Purpose: Assist the client with scheduling an apt with a requested doctor.
        #****************************************************************************
        elif cmd == "SCHEDULE" and len(parts) == 5:
            docName = parts[1]
            timeBlock = parts[2]
            illness = parts[3]
            patHash = parts[4]
            suffixHash = patHash[-5:]
            
            print(f"Hospital Server has received a schedule request from a user with hash suffix: {suffixHash} to book an appointment using TCP over port {TCP_PORT}.")
            
            udpMessage = "SCHEDULE," + docName + "," + timeBlock + "," + patHash + "," + illness
            udpSock.sendto(udpMessage.encode('utf-8'), (HOST, APT_PORT))
            print("Hospital Server has sent the schedule request to the appointment server.")
            
            aptReplyBytes, aptSender = udpSock.recvfrom(1024)
            aptReply = aptReplyBytes.decode('utf-8')
            print(f"Hospital Server has received the response from Appointment Server using UDP over {UDP_PORT}.")
            
            clientConn.send(aptReply.encode('utf-8'))
            print("The hospital server has sent the response to the client.")

        #**************************************************************************** # Purpose: Help the client cancel an appointment they already have/made.
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

        #**************************************************************************** # Purpose: Help the patient lookup a specific apt 
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

        #**************************************************************************** # Purpose: Allow the doctor to view all their scheduled appointments.
        #****************************************************************************
        elif cmd == "VIEW_DOC" and len(parts) == 2:
            docName = parts[1]
            
            print(f"Hospital Server has received a view appointments request from {docName} to view their details using TCP over port {TCP_PORT}.")
            
            udpMessage = "VIEW_DOC," + docName
            udpSock.sendto(udpMessage.encode('utf-8'), (HOST, APT_PORT))
            print("The hospital server has sent the view appointments request to the Appointment Server.")
            
            aptReplyBytes, aptSender = udpSock.recvfrom(1024)
            aptReply = aptReplyBytes.decode('utf-8')
            print(f"Hospital server has received the response from the Appointment server using UDP over port {UDP_PORT}.")
            
            clientConn.send(aptReply.encode('utf-8'))
            print("The hospital server has sent the response to the client.")

        #**************************************************************************** # Purpose: Handle the complex PRESCRIBE command (Doctors only).
        #****************************************************************************
        elif cmd == "PRESCRIBE" and len(parts) == 4:
            docName = parts[1]
            patHash = parts[2]
            freq = parts[3]
            suffixHash = patHash[-5:]
            
            print(f"Hospital Server has received a prescription request from {docName} for a user with hash suffix {suffixHash} using TCP over port {TCP_PORT}.")
            
            # STEP 1: Fetch Illness from the Appointment Server
            udpMessage = "FETCH_ILL," + patHash + "," + docName
            udpSock.sendto(udpMessage.encode('utf-8'), (HOST, APT_PORT))
            print(f"Hospital Server has sent a request to fetch patients with hash suffix {suffixHash} illness information to the Appointment Server.")
            
            aptReplyBytes, aptSender = udpSock.recvfrom(1024)
            aptReply = aptReplyBytes.decode('utf-8')
            print(f"Hospital Server has received the illness response from the Appointment server using UDP over port {UDP_PORT}.")
            
            aptParts = aptReply.split(",")
            
            if aptParts[0] == "FOUND":
                illness = aptParts[1]
                print(f"Acquiring treatment for {illness} from the database.")
                
                if illness in treatments:
                    treatment = treatments[illness]
                    
                    # STEP 3: Send the prescription details to the Prescription Server
                    udpMessage = "PRESCRIBE," + docName + "," + patHash + "," + treatment + "," + freq
                    udpSock.sendto(udpMessage.encode('utf-8'), (HOST, PRES_PORT))
                    print(f"Hospital server has sent the prescription request to the prescription server to prescribe {treatment}.")
                    
                    presReplyBytes, presSender = udpSock.recvfrom(1024)
                    presReply = presReplyBytes.decode('utf-8')
                    print(f"Hospital server has received the response from the prescription server using UDP over port {UDP_PORT}")
                    
                    if presReply == "SUCCESS":
                        clientConn.send(f"SUCCESS,{treatment}".encode('utf-8'))
                    else:
                        clientConn.send("FAILED".encode('utf-8'))
                else:
                    clientConn.send("FAILED".encode('utf-8'))
            else:
                clientConn.send("FAILED".encode('utf-8'))
            
            print("The hospital server has sent the response to the client.")

        #**************************************************************************** # Purpose: Allow a PATIENT to view their own prescription.
        #****************************************************************************
        elif cmd == "VIEW_RX_PAT" and len(parts) == 2:
            patHash = parts[1]
            suffixHash = patHash[-5:]
            
            print(f"Hospital Server has received a prescription request from a patient with hash suffix {suffixHash} to view their prescription details using TCP over port {TCP_PORT}.")
            
            udpMessage = "VIEW_RX," + patHash
            udpSock.sendto(udpMessage.encode('utf-8'), (HOST, PRES_PORT))
            print("Hospital Server has sent the prescription request to the Prescription Server.")
            
            presReplyBytes, presSender = udpSock.recvfrom(1024)
            presReply = presReplyBytes.decode('utf-8')
            print(f"Hospital server has received the response from the prescription server using UDP over port {UDP_PORT}.")
            
            clientConn.send(presReply.encode('utf-8'))
            print("Hospital server has sent the response to the client.")

        #**************************************************************************** # Purpose: Allow a DOCTOR to view a specific patient's prescription.
        #****************************************************************************
        elif cmd == "VIEW_RX_DOC" and len(parts) == 3:
            docName = parts[1]
            patHash = parts[2]
            suffixHash = patHash[-5:]
            
            print(f"Hospital Server has received a prescription request from {docName} to view a patient with hash suffix {suffixHash} prescription details using TCP over port {TCP_PORT}.")
            
            udpMessage = "VIEW_RX," + patHash
            udpSock.sendto(udpMessage.encode('utf-8'), (HOST, PRES_PORT))
            print("Hospital Server has sent the prescription request to the Prescription Server.")
            
            presReplyBytes, presSender = udpSock.recvfrom(1024)
            presReply = presReplyBytes.decode('utf-8')
            print(f"Hospital server has received the response from the prescription server using UDP over port {UDP_PORT}.")
            
            clientConn.send(presReply.encode('utf-8'))
            print("Hospital server has sent the response to the client.")

        # Always close the TCP connection when finished serving the current request
        clientConn.close()

# Basic Ctrl C interrupt 
except KeyboardInterrupt:
    print("\nShutting down Hospital Server...")
finally: 
    tcpSock.close()
    udpSock.close()