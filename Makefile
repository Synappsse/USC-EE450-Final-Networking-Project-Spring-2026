#****************************************************************************
#Purpose: Make all the files in the project 
#Resources: https://www.cs.swarthmore.edu/~newhall/unixhelp/howto_makefiles.html
#https://stackoverflow.com/questions/1062436/python-script-executed-with-makefile
#****************************************************************************

#Make all sets up all the files
all: client hospital_server authentication_server appointment_server prescription_server

client: client.py
	echo '#!/bin/bash' > client
	echo 'python3 client.py "$$@"' >> client
	chmod +x client

hospital_server: hospital_server.py
	echo '#!/bin/bash' > hospital_server
	echo 'python3 hospital_server.py "$$@"' >> hospital_server
	chmod +x hospital_server

authentication_server: authentication_server.py
	echo '#!/bin/bash' > authentication_server
	echo 'python3 authentication_server.py "$$@"' >> authentication_server
	chmod +x authentication_server

appointment_server: appointment_server.py
	echo '#!/bin/bash' > appointment_server
	echo 'python3 appointment_server.py "$$@"' >> appointment_server
	chmod +x appointment_server

prescription_server: prescription_server.py
	echo '#!/bin/bash' > prescription_server
	echo 'python3 prescription_server.py "$$@"' >> prescription_server
	chmod +x prescription_server

#Make clean clears all the files
clean:
	rm -f client hospital_server authentication_server appointment_server prescription_server