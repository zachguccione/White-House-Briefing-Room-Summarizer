import time
import subprocess

while True:
    # Run your script
    subprocess.run(["python", "script.py"])  # Replace with your script's name
    
    # Wait for 10 minutes (600 seconds)
    time.sleep(600)
