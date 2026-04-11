import socket
import sys

#****************************************************************************
#Purpose: Reads the prescriptions.txt file then stores it in a list for use 
#open the prescriptions.txt file and input it into our list var, strip each 
#line of whitespace and ignore blank lines
#****************************************************************************

def createPresList():
    presList = []
    try:
        txtFile = open("prescriptions.txt", "r")
        for line in txtFile:
            line = line.strip()
            if line == "":
                continue

            #Split the read file into 4 individual segments per none empty line
            #Each item in out preList becomes a dictionary with the mandatory info
            parts = line.split(",")
            if len(parts) == 4:
                rx = {
                    "doctor": parts[0],
                    "patientHash": parts[1],
                    "treatment": parts[2],
                    "frequency": parts[3]
                }
                presList.append(rx) 

        txtFile.close()
    
    except FileNotFoundError:
        print("Error: prescriptions.txt not there.")
        
    return presList

#****************************************************************************
#Purpose: Used to add a new prescription to a patient.
#Open the prescriptions list and appends the newest prescription to the botton 
#of the file in our 4 coloumn format.
#****************************************************************************
def addNewPres(docName, patHash, treatment, frequency):
    try:
        txtFile = open("prescriptions.txt", "a")
        
        # Using commas to seperate the precriptions to account for first precription failing
        newPres = f"{docName},{patHash},{treatment},{frequency}\n"
        txtFile.write(newPres)
        txtFile.close()
        
    except Exception as e:
        print("Error saving to prescriptions.txt:", e)

#****************************************************************************
# Purpose: Define constants and bind the UDP socket.
#****************************************************************************
HOST = '127.0.0.1' 
UDP_PORT = 22916 #My SID

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, UDP_PORT))

#Boot message test
print(f"Prescription Server is up and running using UDP on port {UDP_PORT}.")

#****************************************************************************
# Purpose: Begin the loop for grabbing prescriptions
#****************************************************************************
try:
    # Keep looping for data TEST
    while True:
        data, sender = sock.recvfrom(1024)
        
        #Decode and properly segment the information being recieved
        request_str = data.decode('utf-8')
        parts = request_str.split(",")
        cmd = parts[0] #Attempt to understand what the user wants and stores it
        response = "" #setup a response flag for the user in order to help them respond to our response

        #If the user wants to be prescribed something, we need as much info as possible on it
        #Once we grab the info, print the success to the user and append the prescription to our prescriptions.txt
        if cmd == "PRESCRIBE" and len(parts) == 5:
            docName = parts[1]
            patHash = parts[2]
            treatment = parts[3]
            frequency = parts[4]
            suffixHash = patHash[-5:] # Get the last 5 characters
            
            print(f"Prescription Server has received a request from {docName} to prescribe the user with hash suffix {suffixHash}.")
            addNewPres(docName, patHash, treatment, frequency)
            print(f"Successfully saved the prescription details for user with hash suffix: {suffixHash}.")
            response = "SUCCESS"

        #If the user instead wishes to view their current precriptions we seperate the command into 2 parts
        #Then we pull up the most recent prescription file  and search through it for a hash that matches our patient
        elif cmd == "VIEW_RX" and len(parts) == 2:
            patHash = parts[1]
            suffixHash = patHash[-5:]
            
            print(f"The prescription server has received a request to view the prescription for the user with hash suffix: {suffixHash}.")
            
            
            allPrescriptions = createPresList()
            foundRx = None #remains false unless patient has prescription
            for rx in allPrescriptions:
                if rx["patientHash"] == patHash:
                    foundRx = rx
                    
            if foundRx is None:
                print("There are no current prescriptions for this user.")
                response = "NOT_FOUND"
            else:
                if foundRx["frequency"] == "None":
                    print("There are no current prescriptions for this user.")
                else:
                    print("A prescription exists for this user.")
                response = f"FOUND,{foundRx['doctor']},{foundRx['treatment']},{foundRx['frequency']}"
        
        #Respond back to the hospital server with an update to the request
        sock.sendto(response.encode('utf-8'), sender)

#Basic Ctrl C interupt
except KeyboardInterrupt:
    print("\nShutting down Prescription Server...")
finally: 
    sock.close()
