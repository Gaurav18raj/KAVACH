import subprocess
import sys
import time

print("[*] Starting server...")
server = subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.main:app", "--port", "8000"])
time.sleep(3)

try:
    print("[*] Running tests...")
    subprocess.check_call([sys.executable, "advanced_test_kavach.py"])
finally:
    print("[*] Killing server...")
    server.terminate()
    server.wait()
