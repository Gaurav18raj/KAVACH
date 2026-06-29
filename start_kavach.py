import os
import sys
import subprocess
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# We use standard ASCII characters to avoid any Unicode/Emoji errors on Windows CMD/macOS
def print_banner():
    banner = """
================================================================================
                               [ K A V A C H ]
                 AI-Driven Behavioral Authentication Engine
================================================================================
PROJECT OVERVIEW:
 * Secures digital banking channels against Jamtara-style social engineering.
 * Analyzes Behavioral DNA (typing rhythm, device haptics, hold times) in real-time.
 * Zero-Trust Continuous Authentication using Privacy-Preserving Edge Compute.
 * 100% compliant with RBI Data Minimization Guidelines.

CREDITS & ORGANIZATION:
 * Developed By: Deepak Kumar Ravi, Gaurav Raj, and Umesh Gupta
 * Organization: PSB Hackathon by MNNIT Allahabad
================================================================================
"""
    print(banner)

def prompt_install_dependencies():
    REQUIRED_PACKAGES = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "passlib",
        "bcrypt",
        "python-jose",
        "colorama",
        "requests"
    ]
    print("[?] Would you like to check and install required Python libraries? (y/n)")
    choice = input(" > ").strip().lower()
    
    if choice == 'y':
        print("\n[*] Installing dependencies... Please wait.")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + REQUIRED_PACKAGES)
            print("[+] All dependencies installed successfully!\n")
        except subprocess.CalledProcessError as e:
            print(f"[!] Error installing dependencies: {e}")
            print("[!] Please install them manually.\n")
    else:
        print("[*] Skipping dependency installation. Assuming environment is ready.\n")

def check_environment():
    try:
        import fastapi
        import sqlalchemy
    except ImportError:
        print("[!] CRITICAL ERROR: Core libraries missing. Please restart and choose 'y' to install.")
        sys.exit(1)
        
    if not os.path.exists("frontend/index.html"):
        print("[!] ERROR: Frontend directory missing or incomplete! Are you in the right folder?")
        sys.exit(1)
        
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

def start_server():
    print("\n[*] Booting Unified KAVACH Server (Frontend + Backend API)...")
    print("> Web Portal: http://localhost:8000")
    print("> API Docs:   http://localhost:8000/docs")
    print("--------------------------------------------------------------------------------")
    print("[+] SYSTEM LIVE. Monitoring all behavioral endpoints. Press Ctrl+C to stop.\n")
    
    try:
        import uvicorn
        uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, log_level="warning")
    except KeyboardInterrupt:
        print("\n[*] Shutting down KAVACH Server gracefully. Returning to menu...")

def run_automated_tests():
    print("\n[*] Booting ML Automation Test Engine...")
    if not os.path.exists("advanced_test_kavach.py"):
        print("[!] ERROR: advanced_test_kavach.py not found.")
        return

    # The tests need the server running, so we spawn it in the background briefly
    print("[*] Starting temporary KAVACH backend server for testing...")
    server_process = subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.main:app", "--port", "8000"], 
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3) # Wait for server to boot

    try:
        print("[*] Running Advanced Attack Scenarios...\n")
        subprocess.check_call([sys.executable, "advanced_test_kavach.py"])
    except subprocess.CalledProcessError:
        print("\n[!] Tests encountered an error.")
    finally:
        print("\n[*] Shutting down temporary testing server.")
        server_process.terminate()
        server_process.wait()
        print("[+] Tests completed. Returning to menu...")

def run_kli_demo():
    print("\n[*] Initializing Kavach Ledger Intelligence (KLI) Demo...")
    if not os.path.exists("seed_demo_data.py") or not os.path.exists("simulate_kli_attack.py"):
        print("[!] ERROR: KLI demo scripts not found.")
        return

    # Seed the DB
    try:
        subprocess.check_call([sys.executable, "seed_demo_data.py"])
    except subprocess.CalledProcessError:
        print("\n[!] Error seeding database.")
        return

    # Start the server temporarily
    print("\n[*] Starting temporary KAVACH backend server for testing...")
    server_process = subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.main:app", "--port", "8000"], 
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3) # Wait for server to boot

    try:
        print("[*] Running Financial Ledger Attack Scenarios...\n")
        subprocess.check_call([sys.executable, "simulate_kli_attack.py"])
    except subprocess.CalledProcessError:
        print("\n[!] Simulation encountered an error.")
    finally:
        print("\n[*] Shutting down temporary testing server.")
        server_process.terminate()
        server_process.wait()
        print("[+] KLI Demo completed. Returning to menu...")

def main_menu():
    while True:
        print("\n================================================================================")
        print("                            [ MAIN MENU ]")
        print("================================================================================")
        print("1. Start Live KAVACH Server (Web Demo)")
        print("2. Run Automated ML Attack Tests (Good User vs Jamtara Hacker)")
        print("3. Seed KLI Profiles & Run 5-Friends Demo (Financial Ledger)")
        print("4. Exit KAVACH")
        print("================================================================================")
        
        choice = input("Select an option (1-4) > ").strip()
        
        if choice == '1':
            start_server()
        elif choice == '2':
            run_automated_tests()
        elif choice == '3':
            run_kli_demo()
        elif choice == '4':
            print("\n[*] Exiting KAVACH. Goodbye!")
            sys.exit(0)
        else:
            print("[!] Invalid choice. Please select 1, 2, 3, or 4.")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    os.chdir(BASE_DIR)
    clear_screen()
    print_banner()
    prompt_install_dependencies()
    check_environment()
    main_menu()
