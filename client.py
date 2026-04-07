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
# Purpose:Main loop for client once authenticated into our system.
#Here we can run apts, look for precriptions, lookup doctors etc.
#****************************************************************************


#WIll leave for tomorrow




#Basic error handling or Ctrl C interrupt     
except ConnectionRefusedError:
    print("Error: Could not connect to the Hospital Server. Make sure it is running!")
except KeyboardInterrupt:
    print("\nClient shutting down.")
finally:
    clientSock.close()