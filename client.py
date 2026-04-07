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
        
        #Check first to see the userrole before processing their needs
        #If the user is not a patient we will simply move onto to check if they are a doctor
        #If the command is not user specific, the command will be passed on 
        if userRole == "patient":
            
            if mainCmd == "view_appointment":
                pass
           
            elif mainCmd == "view_prescription":
                pass
           
            elif mainCmd == "lookup":
                pass
           
            elif mainCmd == "schedule":
                pass
           
            elif mainCmd == "cancel":
                pass
    
            elif mainCmd == "help":
                print("Please enter the command:\n<lookup>,\n<lookup <doctor>>,\n<schedule <doctor> <start_time> <illness>>,\n<cancel>,\n<view_appointment>,\n<view_prescription>,\n<quit>")
           
            else:
                print("Invalid command. Please type 'help' to see the available options.")

        #Doctor commands
        elif userRole == "doctor":
           
            if mainCmd == "view_appointments":
                pass
           
            elif mainCmd == "view_prescription":
                pass
           
            elif mainCmd == "prescribe":
                pass
            
            elif mainCmd == "help":
                 print("Please enter the command:\n<view_appointments>,\n<prescribe <patient> <frequency>>,\n<view_prescription <patient>>,\n<quit>")
           
            else:
                print("Invalid command. Please type 'help' to see the available options.")

        #Basic quit command
        if mainCmd == "quit":
            print("You have successfully been logged out.")
            print("-Quit Program-")
            break
               
                
 

#Basic error handling or Ctrl C interrupt     
except ConnectionRefusedError:
    print("Error: Could not connect to the Hospital Server. Make sure it is running!")
except KeyboardInterrupt:
    print("\nClient shutting down.")
finally:
    clientSock.close()