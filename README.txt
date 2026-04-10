#*********************************************#
EE 450 Spring 2026 Socket Programming Project
#*********************************************#

A) 

Gabriel Bunny

B) 

6338308916

C) 

This program is a simulation of managing patients and doctors in a hospital setting. We begin the program by setting up all 4 backend servers to run. These MUST be in order. Once setup, we can begin the client server and enter the credentials of a patient/doctor to properly begin. I have set up the program so that multiple clients can be logged in at once. This allows patients and doctors to see real time updates on their ends.

Once the credentials are sent over, they are hashed then compared via the authentication server. The hospital server routes all the communications and acts as an intermediary for the client and the respective servers doing the work.

Once authenticated, the user will receive different options based on their role (doctor or patient). Clients can enter the help command to allow them to see what commands they may enter 

Patients can manage their appointments, check their prescriptions, and lookup the availability of different doctors on file.

Doctors can view their appointments, prescribe medications and lookup in place prescriptions.

All of my work and documentation can be found at: https://github.com/Synappsse/USC-EE450-Final-Networking-Project-Spring-2026


D)

	authentication_server.py:
			Authenticates hashed credentials that are given by comparing them to users.txt. Does not edit users.txt.

	appointment_server.py:
			Opens and parses the appointments.txt files in order to manage client requests for looking up doctors as well as scheduling and cancelling 							appointments. Edits appointments.txt based on new updates.

	prescription_server.py:
			Opens the prescriptions.txt file to look at and return specific patient prescriptions. Updates the txt file based on changes to the patients 						prescription list.
		
	hospital_server.py:	
			Main backend server that communicates with other backend servers and acts as the bridge for the client's program. Once the hospital server receives a 					quest, it will forward it to the correct server then retrieve a response. Based on the response it will give an appropriate reply to the client.
	client.py:
			Program for patient/doctor interface. Users will input their credentials here and the program will hash it and send that to the backend servers. Once 					authenticated, users will be given options such as looking at prescriptions, scheduling appointments etc.



E)


Everything between the client and server will be sent as encoded strings. If there are multiple params to send over between different servers, they will be turned into a concatenated string delimited by a comma.

Formatting:

	Authentication (Client -> Hospital -> Auth Server): 
		<username_hash>,<password_hash>
		#This specifically must have a "" around the password if there is a !
		#Though generally I did not use "" for the input

	uthentication Response (Auth Server -> Hospital -> Client): 
		SUCCESS or FAILED

	Lookup Request (Hospital -> Appointment Server):
		 LOOKUP_DOC,<doctor_username>
	
	Schedule Request (Hospital -> Appointment Server): 	
	
		SCHEDULE,<doctor_username>,<time_block>,<patient_hash>,<illness>`
	
	Cancel Request (Hospital -> Appointment Server):
		CANCEL,<patient_hash>
	
	Fetch Illness Request (Hospital -> Appointment Server): 	
		FETCH_ILLNESS,<patient_hash>,<doctor_username>`

	Prescribe Request (Hospital -> Prescription Server): 							
		PRESCRIBE,<doctor_username>,<patient_hash>,<treatment>,<frequency>
	
	View Prescription (Hospital -> Prescription Server): 
		VIEW_RX,<patient_hash>

F)

Obviously, the code will fail if you do not run the servers in the correct order. You also should not be missing any of the .txt or .py files. I did not make any extra .h files.

I was a little new to making Makefiles for Python projects on Unix, so there might be something that breaks somewhere along the line.

As discussed in some of the Piazza posts, there are certain edge cases that weren't accounted for in the PDF instructions. I did my best with them and just put in the generic failure cases for those. I know however those won't be tested.

I had some trouble fighting with command lengths and reading them over such as whether to have the client type in Dr.X or Dr. X. I should have fixed this but there might be an error relating to it somewhere. Particularly code dealing with the length of an inserted command I am not too confident in. 

G)

I copy pasted the Sha256 hash for Python from the instruction pdf.

I did look online about Makefiles as it has been a while since I made one. I used the provided website on the pdf: https://www.cs.swarthmore.edu/~newhall/unixhelp/howto_makefiles.html.
I also looked online because I wasn't sure on how to set it up for Python running on Ubuntu specifically. 

I used some of Beej's guide for Python such as the striping/splitting functions. It has been a little while since I wrote a program in Python and needed a refresher on basic functions.

Most of the socket and network logic comes from the Beej's Guide to Network content shared on the Brightspace. This includes the sending/receiving from/sendall functions. I added comments explaining what chapter I pulled some of these from in the programs.

I especially had no clue what to do about running multiple clients at once. I used the Beej's guide to learn about threading. That was used heavily in the hospital server, as it was the main server handling multiple connections.

Lastly, I wanted to mention that some of the code I typed is built off of my knowledge from EE250 and ITP/TAC 115. This may include the way I created the sockets and added comments in regards to purpose/resources used for a block of code. I did not directly copy/paste anything from them but did use it as a base. The code should be the same/similar as the Beej Guides.

H)     

I built the code on Windows 11 and tested on the docker container, editing as I went. All final tests were run using the provided csci104 docker container. 
        
