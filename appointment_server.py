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

# #****************************************************************************
#Purpose: Begin the infinite loop while the apt server is up and running
#awaiting insructions from the other servers running and react based on their request
# #****************************************************************************
try:

    while True:
        data, sender = sock.recvfrom(1024)
        
        #Decode the recieved data and pull up the most recent version of the apts schedueled
        request_str = data.decode('utf-8')
        parts = request_str.split(",")
        cmd = parts[0]
        schedule = aptView()
        response = ""

      
        #Basic lookup command of all doctors and their available time slots 
        if cmd == "LOOKUP_ALL" and len(parts) == 1:
            # Updated to match Table 4 exactly
            print("The Appointment Server has received a doctor availability request.")
            availableDocs = ""
            
            # Loop through every doctor to see if they have at least one open slot
            for doc in schedule:
                hasFreeSlot = False
                for timeBlock in schedule[doc]:
                    if schedule[doc][timeBlock] == None:
                        hasFreeSlot = True
                        break # Found availble timeslot, stop move on
                
                if hasFreeSlot == True:
                    availableDocs = availableDocs + doc + "," #Append the free doctor to the list to send back to client
           
            #IF at least one of our doctors is free, let the client know
            if availableDocs != "":
                availableDocs = availableDocs[:-1] 
                response = "AVAILABLE_DOCS," + availableDocs
            else:
                response = "NONE_AVAILABLE"
                
            print("The Appointment Server has sent the lookup result to the Hospital Server.")

        # Basic doctor lookup command
        elif cmd == "LOOKUP_DOC" and len(parts) == 2:
            docName = parts[1]
            print("The Appointment Server has received a doctor availability request.")
            
            #If the doctor exists, lookup their availability
            if docName in schedule:
                freeTimes = ""
                freeCount = 0
                for t in schedule[docName]:
                    if schedule[docName][t] == None:
                        freeTimes = freeTimes + t + ","
                        freeCount = freeCount + 1 #Update the doctor's availability in our variable and prepare to send to client
                
                #Fancier editing to let patient know of available times based on doctor's schedule 
                if freeCount == 8:
                    print(f"All time blocks are available for {docName}.")
                    response = "ALL_AVAILABLE"

                elif freeCount > 0:
                    print(f"{docName} has some time slots available.")
                    freeTimes = freeTimes[:-1] 
                    response = "AVAILABLE," + freeTimes

                else:
                    print(f"{docName} has no time slots available.")
                    response = "NONE_AVAILABLE"
            else: #If the doctor DNE, act like they have no available time slots
                print(f"{docName} has no time slots available.")
                response = "NOT_FOUND"
                
            
            print("The Appointment Server has sent the lookup result to the Hospital Server.")

        # Basic apt schedueling command
        #Breaks request into different parts: doctor, time, patient's hash, patient's illness and, the suffix hash
        elif cmd == "SCHEDULE" and len(parts) == 5:
            docName = parts[1]
            timeBlock = parts[2]
            patHash = parts[3]
            illness = parts[4]
            suffixHash = patHash[-5:] 
            
            print(f"Appointment scheduling request received (time: {timeBlock}, doctor: {docName}, patient hash suffix: {suffixHash}, illness: {illness}).")
        
            #Confirm that doctor exists, and is on the schedule currently
            if docName in schedule and timeBlock in schedule[docName]:
                
                
                #Confirms that the doctor is available at the requested time of patient
                if schedule[docName][timeBlock] == None:
                    schedule[docName][timeBlock] = (patHash, illness)
                    updateSchedule(schedule)
                    print(f"Appointment has been scheduled successfully for user {suffixHash} with {docName}.")
                    response = "SUCCESS"
                
                else:
                    print("The requested appointment time is not available.")
                    freeTimes = ""
                    for t in schedule[docName]:
                        if schedule[docName][t] == None:
                            freeTimes = freeTimes + t + "," #Update the list of available times to offer the patient
                            
                    if freeTimes != "": #If there are already free times for the doctor, let the user know that they have other options
                        freeTimes = freeTimes[:-1]
                        response = "UNAVAILABLE," + freeTimes
                    else:#If the doctor is booked, just say nothing
                        response = "UNAVAILABLE,NONE"
            else:
                response = "FAIL"

        # Basic command to cancel an apt
        elif cmd == "CANCEL" and len(parts) == 2:
            patHash = parts[1]
            suffixHash = patHash[-5:]
            found = False
            
            #Goes through the doctors in the schedule and confirms if they have an apt with our current patient
            #Once the apt is found, cancel it and break
            for doc in schedule:
                for timeBlock in schedule[doc]:
                    details = schedule[doc][timeBlock]
                   
                   #Check to see if doctor and patient are going to meet
                    if details != None and details[0] == patHash:
                        schedule[doc][timeBlock] = None #Update the apt so we cancel it
                        found = True

                        updateSchedule(schedule) #Force the program to update the appointment.txt file with the new schedule
                        response = f"SUCCESS,{doc},{timeBlock}"

                        #Update to pdf wants “Successfully cancelled appointment." instead of “Successfully canceled appointment.”?
                        print(f"Appointment Server has received a cancel appointment command for the user with hash suffix: {suffixHash}. Successfully cancelled appointment.")
                        break
                
                if found == True: 
                    break
            
            if found == False:
                print("Error: Failed to find appointment.")
                response = "FAIL"

            # Command to view details relating to the patients apts
            #Sends back the information regarding what doctor and time the apt has
        elif cmd == "VIEW_PAT" and len(parts) == 2:
            patHash = parts[1]
            suffixHash = patHash[-5:]
            print(f"Appointment Server has received a view appointment command for the user with hash suffix {suffixHash}.")
            found = False
            
            #Checks each doctor on the schedule and their apts. If the details of the apt have the patients hash, we know that the 2 are schedueled for an apt
            #Once we confirm a patient and doctor are to meet, we can send that back to the server
            for doc in schedule:
                for timeBlock in schedule[doc]:
                    details = schedule[doc][timeBlock]

                    if details != None and details[0] == patHash: #IF the doctor has an apt and that apt matches the patients hash, we got a match
                        found = True

                        response = f"FOUND,{doc},{timeBlock}"
                        print(f"Returning details regarding the appointment for the user with hash suffix {suffixHash}.")
                        break
                
                if found == True: 
                    break
                    
            if found != True:
                print(f"The user with hash suffix {suffixHash} has no appointment in the system.")
                response = "NOT_FOUND"

        #Command to view what appointments a doctor currently has
        #We open up our schedule again to see when the doctor is booked and add it to their booked times
        elif cmd == "VIEW_DOC" and len(parts) == 2:
            docName = parts[1]
            print(f"Appointment Server has received a request to view appointments scheduled for {docName}.")
            
            if docName in schedule:
                bookedTimes = ""

                for t in schedule[docName]:
                    if schedule[docName][t] != None:
                        bookedTimes = bookedTimes + t + ","   #Adds the apt to the doctors time if it exists

                if bookedTimes != "": #Then we check the list of times and edit it properly
                    bookedTimes = bookedTimes[:-1] 
                    print(f"Returning the scheduled appointments for {docName}.")
                    response = "BOOKED," + bookedTimes
                else:
                    print(f"No appointments have been made for {docName}.")
                    response = "NONE"
            else:
                response = "NONE"

        # If told to get the illness for a precription, we will hash the 2 parts of the command 
        #Then we will compare first with the doctors name and see if they are schedueled 
        #After that we will see what illness the patient has
        elif cmd == "FETCH_ILL" and len(parts) == 3:
            patHash = parts[1]
            docName = parts[2]
            suffixHash = patHash[-5:]
            print(f"Appointment Server has received a request from Hospital Server regarding information about a user with hash suffix {suffixHash} from {docName}.")
            
            #Set up enmpty vars to grab info on illness of patient
            patIllness = ""
            patTime = ""
            
            if docName in schedule:
                #To check for the doctor, we see if he is busy or not
                for timeBlock in schedule[docName]:
                    details = schedule[docName][timeBlock]
                    if details != None and details[0] == patHash: #check if the patients hash is in the apt time 
                        patIllness = details[1] #add the details of the patients illness
                        patTime = timeBlock
                        # Free the schedule up for later use
                        schedule[docName][timeBlock] = None 
                        break

            #Final check to see if patient has an illness and if so, will update the schedule 
            #If there is no illness, update the response but do nothing else           
            if patIllness != "":
                print("Sending back the requested information to the Hospital server.")
                print(f"Successfully removed {suffixHash} appointment slot, {patTime} is now free to be scheduled for tomorrow.")
                
                # Save the updated schedule showing the empty slot
                updateSchedule(schedule)
                response = f"FOUND,{patIllness}"
            else:
                response = "NOT_FOUND"
                
        sock.sendto(response.encode('utf-8'), sender)

#Basic Ctrl C interupt      
except KeyboardInterrupt:
    print("\nShutting down Appointment Server...")
finally: 
    sock.close()