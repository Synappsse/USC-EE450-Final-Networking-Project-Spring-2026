import socket
import sys
import hashlib

#****************************************************************************
# Resources Used: Instructions pdf from Brightspace
# Purpose: Removes white/trailing space and allows me to use the SHA256 stuff
#****************************************************************************
def sha256_hash(text: str) -> str:
    text = text.strip()
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

#****************************************************************************
# Purpose: Grab the authentication request from the client.py startup arg
#****************************************************************************
# Grab command line arguments
# sys.argv[0] is the script name, sys.argv[1] is username, sys.argv[2] is password
if len(sys.argv) != 3:
    print("Usage: python client.py <username> <password>")
    sys.exit(1)

# Store the raw username/password for our print statements
# Hash them immediately to send over the network
username = sys.argv[1]
password = sys.argv[2]
userHash = sha256_hash(username)
passHash = sha256_hash(password)

#****************************************************************************
# Purpose: Define constants and connect to the hospital server
#****************************************************************************
HOST = '127.0.0.1' 
HOSPITAL_TCP_PORT = 26916 #My SID

print("The client is up and running.")
clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Main part to attempt connecting to the hospital server. 
#This begins with our connection then the authentication using the AUTH flag sent to the hospital server
try:
    
    clientSock.connect((HOST, HOSPITAL_TCP_PORT))
    authMessage = "AUTH," + userHash + "," + passHash
    clientSock.send(authMessage.encode('utf-8'))
    
   
   #Once we send over the request, set up a variable to catch the response
    print(f"{username} sent an authentication request to the hospital server.")
    replyBytes = clientSock.recv(1024)
    authReply = replyBytes.decode('utf-8')
    
    #Confirm if the client is a patient or a doctor. Set up a userRole variable for later options and the next response
    if authReply == "SUCCESS_PAT":
        print(f"{username} received the authentication result. Authentication successful. You have been granted patient access.")
        userRole = "patient"    
    elif authReply == "SUCCESS_DOC":
        print(f"{username} received the authentication result. Authentication successful. You have been granted doctor access.")
        userRole = "doctor"
    #If the credentials are wrong, simply tell the user and keep running the loop   
    else:
        # FAILED or anything else
        print("The credentials are incorrect. Please try again.")
        clientSock.close()
        sys.exit(0) # End the program so they have to run it again, per instructions

#****************************************************************************
# Purpose: Begin main loop once user role designated 
#****************************************************************************

    while True:
        # Take in the next command once authenticated then split it properly and force all lowercase for easier checking
        userInput = input("\nPlease enter a command: ").strip()
        cmdParts = userInput.split()
        mainCmd = cmdParts[0].lower() 
        

        #Basic quit command
        if mainCmd == "quit":
            print("You have successfully been logged out.")
            print("-Quit Program-")
            break

        #Check first to see the userrole before processing their needs
        #If the user is not a patient we will simply move onto to check if they are a doctor
        #If the command is not user specific, the command will be passed on 
        if userRole == "patient":
            
            if mainCmd == "view_appointment":
                print(f"{username} sent a request to view their appointment to the Hospital Server.")
                msg = "VIEW_PAT," + userHash
                clientSock.send(msg.encode('utf-8'))
                
                reply = clientSock.recv(1024).decode('utf-8')
                print(f"The client received the response from the hospital server using TCP over port {clientSock.getsockname()[1]}")
                
                replyParts = reply.split(",")
                if replyParts[0] == "FOUND":
                    print(f"You have an appointment scheduled with {replyParts[1]} at {replyParts[2]}.")
                else:
                    print("You do not have an appointment today.")
           
            elif mainCmd == "view_prescription":
                print(f"{username} sent a request to view their prescription to the Hospital Server.")
                # Using VIEW_RX_PAT so the hospital knows it's the patient asking
                msg = "VIEW_RX_PAT," + userHash
                clientSock.send(msg.encode('utf-8'))
                
                reply = clientSock.recv(1024).decode('utf-8')
                print(f"The client received the response from the hospital server using TCP over port {clientSock.getsockname()[1]}")
                
                replyParts = reply.split(",")
                if replyParts[0] == "FOUND":
                    # If frequency is 'None', the print is slightly different per the rubric
                    if replyParts[3] == "None":
                         print(f"You were not prescribed any treatment by {replyParts[1]} following your diagnosis.")
                    else:
                         print(f"You have been prescribed {replyParts[2]}, to be taken {replyParts[3]}, by {replyParts[1]}.")
                else:
                    print("You do not have a prescription to look up.")
           
           
            elif mainCmd == "lookup":
                # Plain lookup for all doctors
                if len(cmdParts) == 1:

                    print(f"{username} sent a lookup request to the hospital server.")
                    msg = "LOOKUP," + userHash
                    clientSock.send(msg.encode('utf-8'))
                    
                    reply = clientSock.recv(1024).decode('utf-8')
                    print(f"The client received the response from the hospital server using TCP over port {clientSock.getsockname()[1]}.")
                    
                    replyParts = reply.split(",")
                    
                    #If we do pull something, then show our client what doctor is available
                    if replyParts[0] == "AVAILABLE_DOCS":
                        print("The following doctors are available:")
                        
                        for i in range(1, len(replyParts)):
                            print(replyParts[i])
                    else:
                        print("No doctors are currently available.")
                        
                # Lookup for specific doctor
                #Checked to see if length of command is 2 or 3 parts in case someone types Dr.X or Dr. X
                elif len(cmdParts) == 2 or len(cmdParts) == 3:

                    docName = cmdParts[1]
                    print(f"Patient {username} sent a lookup request to the hospital server for {docName}.")
                    
                    msg = "LOOKUP_DOC," + docName + "," + userHash
                    clientSock.send(msg.encode('utf-8'))
                    
                    reply = clientSock.recv(1024).decode('utf-8')
                    print(f"The client received the response from the Hospital Server using TCP over port {clientSock.getsockname()[1]}.")
                    
                    replyParts = reply.split(",")
                   
                    if reply == "ALL_AVAILABLE":
                        
                        print(f"All time blocks are available for {docName}.")
                    
                    elif replyParts[0] == "AVAILABLE":
                        print(f"{docName} is available at times:")
                       
                        for i in range(1, len(replyParts)):
                            print(replyParts[i])
                    
                    elif reply == "NONE_AVAILABLE" or reply == "NOT_FOUND":
                        print(f"{docName} has no time slots available.")
            
            elif mainCmd == "schedule" and len(cmdParts) == 4:
                docName = cmdParts[1]
                timeBlock = cmdParts[2]
                illness = cmdParts[3]
                
                print(f"{username} sent an appointment schedule request to the hospital server.")
                msg = "SCHEDULE," + docName + "," + timeBlock + "," + illness + "," + userHash
                clientSock.send(msg.encode('utf-8'))
                
                reply = clientSock.recv(1024).decode('utf-8')
                print(f"The client received the response from the Hospital Server using TCP over port {clientSock.getsockname()[1]}")
                
                replyParts = reply.split(",")
                if reply == "SUCCESS":
                    print(f"An appointment has been successfully scheduled for patient {username} with {docName} at {timeBlock}.")
                elif replyParts[0] == "UNAVAILABLE":
                    if len(replyParts) > 1 and replyParts[1] != "NONE":
                        print(f"Unable to schedule an appointment with {docName} at {timeBlock}. Other available time blocks are")
                        for i in range(1, len(replyParts)):
                            print(replyParts[i])
                    else:
                        print(f"Unable to schedule an appointment with {docName} at this time, as all time blocks have been taken up.")
           
            elif mainCmd == "cancel":
                print(f"{username} sent a cancellation request to the Hospital Server.")
                msg = "CANCEL," + userHash
                clientSock.send(msg.encode('utf-8'))
                
                reply = clientSock.recv(1024).decode('utf-8')
                print(f"The client received the response from the Hospital Server using TCP over port {clientSock.getsockname()[1]}")
                
                replyParts = reply.split(",")
                if replyParts[0] == "SUCCESS":
                    print(f"You have successfully cancelled your appointment with {replyParts[1]} at {replyParts[2]}.")
                else:
                    print("You have no appointments available to cancel.")
        
            elif mainCmd == "help":
                print("Please enter the command:\n<lookup>,\n<lookup <doctor>>,\n<schedule <doctor> <start_time> <illness>>,\n<cancel>,\n<view_appointment>,\n<view_prescription>,\n<quit>")
           
            else:
                print("Invalid command. Please type 'help' to see the available options.")
                
        elif userRole == "doctor":
           
            if mainCmd == "view_appointments":
                print(f"{username} sent a request to view their scheduled appointments to the Hospital Server.")
                msg = "VIEW_DOC," + username 
                clientSock.send(msg.encode('utf-8'))
                
                reply = clientSock.recv(1024).decode('utf-8')
                print(f"The client received the response from the hospital server using TCP over port {clientSock.getsockname()[1]}")
                
                replyParts = reply.split(",")
                if replyParts[0] == "BOOKED":
                    print(f"{username} is scheduled at times:")
                    for i in range(1, len(replyParts)):
                        print(replyParts[i])
                else:
                    print("You do not have any appointments scheduled.")
           
            elif mainCmd == "view_prescription" and len(cmdParts) == 2:
                patName = cmdParts[1]
                patHash = sha256_hash(patName) # Hash the patient's name!
                
                print(f"{username} sent a request to view {patName} prescription to the Hospital Server.")
                msg = "VIEW_RX_DOC," + username + "," + patHash
                clientSock.send(msg.encode('utf-8'))
                
                reply = clientSock.recv(1024).decode('utf-8')
                print(f"The client received the response from the hospital server using TCP over port {clientSock.getsockname()[1]}")
                
                replyParts = reply.split(",")
                if replyParts[0] == "FOUND":
                    docWhoPrescribed = replyParts[1]
                    treatment = replyParts[2]
                    freq = replyParts[3]
                    print(f"{patName} has been prescribed {treatment}, to be taken {freq}, by {docWhoPrescribed}.")
                else:
                    print(f"{patName} does not have a prescription.")
           
            elif mainCmd == "prescribe" and len(cmdParts) == 3:
                patName = cmdParts[1]
                freq = cmdParts[2]
                patHash = sha256_hash(patName) # Hash the patient's name!
                
                print(f"{username} sent a request to the Hospital Server to prescribe {patName} following their diagnosis.")
                
                msg = "PRESCRIBE," + username + "," + patHash + "," + freq
                clientSock.send(msg.encode('utf-8'))
                
                reply = clientSock.recv(1024).decode('utf-8')
                print(f"The client received the response from the hospital server using TCP over port {clientSock.getsockname()[1]}")
                
                replyParts = reply.split(",")
                if replyParts[0] == "SUCCESS":
                    treatment = replyParts[1]
                    print(f"You have successfully prescribed {patName} with {treatment}, to be taken {freq}.")
                else:
                    print("Prescription failed.")
            
            elif mainCmd == "help":
                 print("Please enter the command:\n<view_appointments>,\n<prescribe <patient> <frequency>>,\n<view_prescription <patient>>,\n<quit>")
           
            else:
                print("Invalid command. Please type 'help' to see the available options.")

      
               
                
 

#Basic error handling or Ctrl C interrupt     
except ConnectionRefusedError:
    print("Error: Could not connect to the Hospital Server. Make sure it is running!")
except KeyboardInterrupt:
    print("\nClient shutting down.")
finally:
    clientSock.close()