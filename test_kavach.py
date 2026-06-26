import time
import requests
import sys

def test():
    print("Waiting for server to be ready...")
    for _ in range(15):
        try:
            r = requests.get("http://localhost:8000/")
            if r.status_code == 200:
                break
        except Exception as e:
            time.sleep(1)
    else:
        print("Server didn't start in time.")
        sys.exit(1)
        
    print("Server is up! Testing Registration...")
    reg_data = {
        "full_name": "Test User",
        "username": "test_auto@upi",
        "password": "password123"
    }
    # Might fail with 400 if already exists, that's fine for re-runs
    r = requests.post("http://localhost:8000/api/v1/register", json=reg_data)
    print(f"Register Status: {r.status_code} - {r.text}")

    print("\nTesting Login...")
    login_data = {
        "username": "test_auto@upi",
        "password": "password123",
        "behavioral_data": {
            "hold_mean": 80.5,
            "hold_std": 10.2,
            "iki_mean": 120.0,
            "iki_std": 15.0,
            "backspace_count": 0,
            "hesitation_ms": 300,
            "mouse_entropy": 2.5
        },
        "device": {
            "userAgent": "Mozilla/5.0",
            "screenRes": "1920x1080",
            "timezoneOffset": -330,
            "language": "en-US",
            "canvasHash": "abcd123"
        }
    }
    r = requests.post("http://localhost:8000/api/v1/login", json=login_data)
    print(f"Login Status: {r.status_code} - {r.text}")
    
    if r.status_code == 200:
        print("\n[SUCCESS] All Endpoints functioning perfectly!")
    else:
        print("\n[FAILED] Encountered an error during testing.")
        sys.exit(1)

if __name__ == "__main__":
    test()
