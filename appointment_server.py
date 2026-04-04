import socket
import sys

#****************************************************************************
#Purpose: Helper function to view our appointments
#Opens the appointments.txt file and inserts all the data into a readable 
#dictionary. 
#****************************************************************************
def aptView():
    schedDict = {}
    currentDoc = ""
    
    try:
        aptFile = open("appointments.txt", "r")  
        for line in aptFile:
            line = line.strip()
    
            if line == "":
                continue

            #String split the lines and check to differentiate what the text it  
            parts = line.split()
            if ":" in parts[0]:
                timeBlock = parts[0]

                if len(parts) >= 3: #Check to see if the slot is taken
                    schedDict[currentDoc][timeBlock] = (parts[1], parts[2])
                else:
                    # If slot not taken, update that in our dicitonary
                    schedDict[currentDoc][timeBlock] = None
            else:
                currentDoc = parts[0]
                if currentDoc not in schedDict:
                    schedDict[currentDoc] = {}
                    
        aptFile.close() 
        
    except FileNotFoundError:
        print("Error: appointments.txt not there.")
        
    return schedDict
#****************************************************************************
#Purpose: Helper function to edit our appointments file
#Opens the appointments.txt file and updates it with the newly requested 
#appointment time.
#****************************************************************************
def updateSchedule(schedDict):
    aptFile = open("appointments.txt", "w")
    
    #Go through each doctor/timeblok and update accordingly
    for doc in schedDict:
        aptFile.write(doc + "\n")
        
        for timeBlock in schedDict[doc]:
            details = schedDict[doc][timeBlock] 
            if details != None:
                aptFile.write(timeBlock + " " + details[0] + " " + details[1] + "\n")
            else:
                aptFile.write(timeBlock + "\n")
                
        aptFile.write("\n") #leave a newline after each write     
    aptFile.close()
# #****************************************************************************
# Purpose: Define constants and bind the UDP socket.
# #****************************************************************************
HOST = '127.0.0.1' 
UDP_PORT = 23916 # My SID

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, UDP_PORT))

#Boot message 
print(f"Appointment Server is up and running using UDP on port {UDP_PORT}.")

try:
    # Keep looping for data TEST
    while True:
        data, sender = sock.recvfrom(1024)

#Basic Ctrl C interupt      
except KeyboardInterrupt:
    print("\nShutting down Appointment Server...")
finally: 
    sock.close()