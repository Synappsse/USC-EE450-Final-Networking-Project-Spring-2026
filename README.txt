#*********************************************#
EE 450 Spring 2026 Socket Programming Project
#*********************************************#

A) 

Gabriel Bunny

B) 

6338308916

C) 

This program is a simulation of managing patients and doctors in a hospital setting. We begin the program by setting up all 4 backend servers to run. These MUST be in order. Once setup, we can begin the client server and enter the credentials of a patient/doctor to properly begin.

Once the credentials are sent over, they are hashed then compared via the authentication server. The hospital server routes all the communications and acts as an intermediary for the client and the respective servers doing the work.

Once authenticated, the user will receive different options based on their role (doctor or patient). 

Patients can manage their appointments, check their prescriptions, and lookup the availability of different doctors on file.

Doctors can view their appointments, prescribe medications and lookup in place prescriptions.

All of my work and documentation can be found at: https://github.com/Synappsse/USC-EE450-Final-Networking-Project-Spring-2026


D)

	authentication_server.py:
			Authenticates hashed credentials that are given by comparing them to users.txt. Does not edit users.txt.

	appointment_server.py:
			Opens and parses the appointments.txt files in order to manage client requests for looking up doctors as well as scheduling and cancelling 							appointments. Edits appointments.txt based on new updates.

	prescriptions_server.py:
			Opens the prescriptions.txt file to look at and return specific patient prescriptions. Updates the txt file based on changes to the patients 						prescription list.
	


E)

Formatting:
	Authentication (Client -> Hospital -> Auth Server): 
		<username_hash>,<password_hash>
		#This specifically must have a "" around the password if there is a !
		#Though generally I did not use "" for the input

F)

Obviously, the code will fail if you do not run the servers in the correct order. You also should not be missing any of the .txt or .py files. I did not make any extra .h files.

As discussed in some of the Piazza posts, there are certain edge cases that weren't accounted for in the PDF instructions. I did my best with them and just put in the generic failure cases for those. I know however those won't be tested.


G)

I copy pasted the Sha256 hash for Python from the instruction pdf.

I used some of Beej's guide for Python such as the striping/splitting functions. It has been a little while since I wrote a program in Python and needed a refresher on basic functions.

Most of the socket and network logic comes from the Beej's Guide to Network content shared on the Brightspace. This includes the sending/receiving from/sendall functions. I added comments explaining what chapter I pulled some of these from in the programs.

Lastly, I wanted to mention that some of the code I typed is built off of my knowledge from EE250 and ITP/TAC 115. This may include the way I created the sockets and added comments in regards to purpose/resources used for a block of code. I did not directly copy/paste anything from them but did use it as a base. The code should be the same/similar as the Beej Guides.

H)     

I built the code on Windows 11 and tested on the docker container, editing as I go.                 
        
