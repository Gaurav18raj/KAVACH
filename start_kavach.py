import os
import sys
import subprocess
import uvicorn
import time
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init(autoreset=True)

# Define the required dependencies
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

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = f"""{Fore.CYAN}{Style.BRIGHT}
================================================================================
                               [ K A V A C H ]
                 AI-Driven Behavioral Authentication Engine
================================================================================{Style.RESET_ALL}
{Fore.YELLOW}PROJECT OVERVIEW:{Style.RESET_ALL}
 • Secures digital banking channels against Jamtara-style social engineering.
 • Analyzes Behavioral DNA (typing rhythm, device haptics, hold times) in real-time.
 • Zero-Trust Continuous Authentication using Privacy-Preserving Edge Compute.
 • 100% compliant with RBI Data Minimization Guidelines.

{Fore.GREEN}CREDITS & ORGANIZATION:{Style.RESET_ALL}
 • Developed By: Deepak Kumar Ravi, Gaurav Raj, and Umesh Gupta
 • Organization: PSB Hackathon by MNNIT Allahabad
================================================================================
"""
    print(banner)

def prompt_install_dependencies():
    print(f"{Fore.MAGENTA}[?] Would you like to check and install required Python libraries? (y/n){Style.RESET_ALL}")
    choice = input(" > ").strip().lower()
    
    if choice == 'y':
        print(f"\n{Fore.CYAN}[*] Installing dependencies... Please wait.{Style.RESET_ALL}")
        try:
            # We use subprocess to run pip install
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + REQUIRED_PACKAGES)
            print(f"{Fore.GREEN}[+] All dependencies installed successfully!{Style.RESET_ALL}\n")
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}[!] Error installing dependencies: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[!] Please install them manually.{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.YELLOW}[*] Skipping dependency installation. Assuming environment is ready.{Style.RESET_ALL}\n")

def check_environment():
    try:
        import fastapi
        import sqlalchemy
    except ImportError:
        print(f"{Fore.RED}[!] CRITICAL ERROR: Core libraries missing. Please restart and choose 'y' to install.{Style.RESET_ALL}")
        sys.exit(1)
        
    if not os.path.exists("frontend/index.html"):
        print(f"{Fore.RED}[!] ERROR: Frontend directory missing or incomplete! Are you in the right folder?{Style.RESET_ALL}")
        sys.exit(1)
        
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True) # Directory for kavach_demo.log

def start_server():
    print(f"{Fore.MAGENTA}[?] Good to start the demonstration? (y/n){Style.RESET_ALL}")
    choice = input(" > ").strip().lower()
    
    if choice != 'y':
        print(f"{Fore.RED}[*] Demonstration aborted. Exiting KAVACH...{Style.RESET_ALL}")
        sys.exit(0)

    print(f"\n{Fore.CYAN}[*] Booting Unified KAVACH Server (Frontend + Backend API)...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}> Web Portal: http://localhost:8000{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}> API Docs:   http://localhost:8000/docs{Style.RESET_ALL}")
    print(f"{Fore.BLUE}--------------------------------------------------------------------------------{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[+] SYSTEM LIVE. Monitoring all behavioral endpoints. Press Ctrl+C to stop.{Style.RESET_ALL}\n")
    
    try:
        # Run FastAPI via Uvicorn. "backend.main:app" assumes we run from the project root.
        uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, log_level="warning")
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[*] Shutting down KAVACH Server gracefully. Goodbye!{Style.RESET_ALL}")
        sys.exit(0)

if __name__ == "__main__":
    clear_screen()
    print_banner()
    prompt_install_dependencies()
    check_environment()
    start_server()
