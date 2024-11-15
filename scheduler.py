import time
import subprocess

python_interpreter = r"venv\Scripts\python"  # For Windowsx

while True:
    subprocess.run([python_interpreter, "script.py"])
    time.sleep(600)
