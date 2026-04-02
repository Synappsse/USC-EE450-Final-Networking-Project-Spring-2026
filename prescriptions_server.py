import subprocess
import time
import sys

def main():
    print("Initializing Hospital Network System...")
    print("Opening separate terminal windows for each server...\n")

    # ---------------------------------------------------------
    # Purpose: Define the servers in the exact order required by 
    #          Phase 1A of the EE 450 Guidelines.
    # Source concept: EE 450 Project Guidelines-9.pdf (Process Flow)
    # ---------------------------------------------------------
    servers = [
        "hospital_server.py",
        "authentication_server.py",
        "appointment_server.py",
        "prescription_server.py"
    ]

    processes = []

    # ---------------------------------------------------------
    # Purpose: Loop through the server list and launch them.
    # Source concept for loops: Beej's Guide to Python (Chapter 6)
    # ---------------------------------------------------------
    for server in servers:
        print(f"Starting {server}...")
        
        # subprocess.Popen is a standard Python tool used to spawn new processes.
        # 'cmd.exe /c' tells Windows to open the command prompt.
        # 'start cmd.exe /k' opens a NEW window and keeps it open (/k) so you can read the logs.
        # sys.executable ensures we use the exact same Python version running this script.
        try:
            p = subprocess.Popen(
                f'start cmd.exe /k "{sys.executable} {server}"', 
                shell=True
            )
            processes.append(p)
            
            # Pause briefly to ensure the ports bind in the correct sequence
            time.sleep(1.5)
            
        except Exception as e:
            print(f"Failed to start {server}. Error: {e}")

    print("\n--------------------------------------------------------")
    print("All backend servers have been initiated in separate windows!")
    print("You may now open a final command prompt to run your client:")
    print("Example: python client.py <username> <password>")
    print("--------------------------------------------------------")

if __name__ == "__main__":
    main()