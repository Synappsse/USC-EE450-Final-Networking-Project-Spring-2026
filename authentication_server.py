import socket
import sys
import hashlib #Optional built in use for Python hashing

#****************************************************************************
# Resources Used: Instructions pdf from Brightspace
# Purpose: Removes white/trailing space and allows me to use the SHA256 stuff
#****************************************************************************
def sha256_hash(text: str) -> str:
    text = text.strip()
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

#****************************************************************************
# Resources Used: bgpython_usl_c_1_2025.pdf - Chapter 13.5 and 13.6
# Purpose: Helps me open the users.txt file and stores the output
#****************************************************************************
def accessUsers():
    
    userDict = {} #Create a dictionary of all data taken from our txt file
    try:
        # Taken directly from chapter 13.5 to open and capture the info from users.txt
        #Read text, strip it and split it
        u = open("users.txt", "r")
        
        for line in u:
            line = line.strip()
            
            if line:
                parts = line.split() 
                
                if len(parts) == 2:
                    userDict[parts[0]] = parts[1] 
       
        u.close() #close out the file once done to prevent shennanigans 
    
    # Throw an error if we cannot find the users.txt file, else return what we pulled
    except FileNotFoundError:
        print("Error: users.txt not there.")
    
    return userDict

knownUsers = accessUsers()

# #****************************************************************************
# Purpose: Define constants and bind the UDP socket.
# #****************************************************************************
HOST = '127.0.0.1' # Needed static port assignment  
UDP_PORT = 21916 # 916 are the last 3 digit of my SID

# Set up a UDP socket and bind the socket to the port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, UDP_PORT))
print(f"Authentication Server is up and running using UDP on port {UDP_PORT}.") # Send out a simple boot up message to let user know succesful compile

# #****************************************************************************
# Resources Used: bgnet0_usl_c_1_2025.pdf - Chapter 15.8.1 (Basic socket stuff and how to send reply back)
# Purpose: Keep the authentication server running to catch any login attempts
# #****************************************************************************
try:

    #Contimue to pull data from the socket and split every string to hash properly
    while True:
        data, sender = sock.recvfrom(1024)
        request_str = data.decode('utf-8')
        parts = request_str.split(",") 
        
        if len(parts) == 2:
            #Set up hashes
            nameHash = parts[0]
            passHash = parts[1]
            suffixHash = nameHash[-5:]
            
            print(f"Authentication Server has received an authentication request for a user with hash suffix: {suffixHash}.") 

            #if this user is in our system and correctly inputs their info then proceed
            #if this user is NOT in our system or they have input inocrrect credentials, then we deny them moving forward and keep polling
            if nameHash in knownUsers and knownUsers[nameHash] == passHash: 
                print(f"Authentication succeeded for a user with hash suffix: {suffixHash}.")  
                response = "SUCCESS"
            else:
                print(f"Authentication failed for a user with hash suffix: {suffixHash}.") 
                response = "FAILED"
                
            # Reply to the hospital server to let it know whether the client input was successful. If not, the loop will continue. If it is correct, we will open the menu
            sock.sendto(response.encode('utf-8'), sender)
            print("The Authentication Server has sent the authentication result to the Hospital Server.")

#Simple interupt in case Ctrl C pressed 
except KeyboardInterrupt:
    print("\nShutting down Authentication Server...")

finally: 
    sock.close()