import subprocess
import sys
import time
import webbrowser
import os

def main():
    print("================================================================================")
    print("                               [ K A V A C H ]")
    print("                 AI-Driven Behavioral Authentication Engine")
    print("================================================================================")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))

    print("[*] Starting KAVACH Unified Server (FastAPI on port 8000)...")
    # Start Backend (which also serves the Frontend static files)
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
        cwd=base_dir
    )
    
    print("[*] Waiting for server to initialize...")
    time.sleep(3)

    url = "http://127.0.0.1:8000"
    print(f"[*] Opening KAVACH in your default browser at {url}")
    webbrowser.open(url)
    
    print("\n[+] KAVACH is live! Press Ctrl+C in this terminal to stop the server.")
    
    try:
        # Keep the main thread alive so the user can hit Ctrl+C
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Shutting down server...")
        backend_process.terminate()
        backend_process.wait()
        print("[+] KAVACH successfully shut down.")

if __name__ == "__main__":
    main()
