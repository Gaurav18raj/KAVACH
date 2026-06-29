import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def simulate():
    print("\n==================================================")
    print(" [KLI] KAVACH LEDGER INTELLIGENCE DEMO")
    print("==================================================\n")
    
    # 1. Login as Deepak
    print("[*] Logging in as Deepak...")
    resp = requests.post(f"{BASE_URL}/login", json={
        "username": "deepak@upi",
        "password": "password123",
        "device": {
            "userAgent": "iPhone 15",
            "screenRes": "390x844",
            "canvasHash": "mock_hash_deepak",
            "timezoneOffset": -330,
            "language": "en-IN"
        },
        "behavioral_data": {
            "hold_mean": 90, "hold_std": 10,
            "iki_mean": 150, "iki_std": 20,
            "backspace_count": 0, "hesitation_ms": 100,
            "mouse_entropy": 5, "gyro_angle": 45,
            "transaction_amount": 0.0
        }
    })
    deepak_token = resp.json().get("session_token")
    if not deepak_token:
        print("Failed to login Deepak. Make sure server is running and DB is seeded.")
        return

    # Scenario 1: Deepak's credentials stolen -> sends 2500 to fraudster99@upi
    print("\n--------------------------------------------------")
    print("[SCENARIO 1] Deepak's credentials stolen (Jamtara attack)")
    print("Attacker logs in, tries to send Rs. 2500 to fraudster99@upi")
    print("--------------------------------------------------")
    time.sleep(1)
    
    resp = requests.post(f"{BASE_URL}/transaction", json={
        "username": "deepak@upi",
        "payee_upi": "fraudster99@upi",
        "amount": 2500.0,
        "device": {
            "userAgent": "iPhone 15",
            "screenRes": "390x844",
            "canvasHash": "mock_hash_deepak",
            "timezoneOffset": -330,
            "language": "en-IN"
        },
        "behavioral_data": {
            "hold_mean": 90, "hold_std": 10,
            "iki_mean": 150, "iki_std": 20,
            "backspace_count": 0, "hesitation_ms": 100,
            "mouse_entropy": 5, "gyro_angle": 45,
            "transaction_amount": 2500.0
        }
    }, headers={"Authorization": f"Bearer {deepak_token}"})
    
    # Expected: Blocked
    print(f"Status Code: {resp.status_code}")
    data = resp.json()
    print(f"Action: {data.get('action')}")
    print("Reasons:")
    for r in data.get("reasons", []):
        print(f"  -> {r}")

    # 2. Login as Albert
    print("\n\n[*] Logging in as Albert...")
    resp = requests.post(f"{BASE_URL}/login", json={
        "username": "albert@upi",
        "password": "password123",
        "device": {
            "userAgent": "Samsung S23",
            "screenRes": "1080x2340",
            "canvasHash": "mock_hash_albert",
            "timezoneOffset": -330,
            "language": "en-IN"
        },
        "behavioral_data": {
            "hold_mean": 90, "hold_std": 10,
            "iki_mean": 150, "iki_std": 20,
            "backspace_count": 0, "hesitation_ms": 100,
            "mouse_entropy": 5, "gyro_angle": 45,
            "transaction_amount": 0.0
        }
    })
    albert_token = resp.json().get("session_token")
    
    # Scenario 2: Same ₹2500 from Albert (legitimate)
    print("\n--------------------------------------------------")
    print("[SCENARIO 2] Same Rs. 2500 from Albert (legitimate)")
    print("Albert sends Rs. 2500 to deepak@upi after a night out")
    print("--------------------------------------------------")
    time.sleep(1)
    
    resp = requests.post(f"{BASE_URL}/transaction", json={
        "username": "albert@upi",
        "payee_upi": "deepak@upi",
        "amount": 2500.0,
        "device": {
            "userAgent": "Samsung S23",
            "screenRes": "1080x2340",
            "canvasHash": "mock_hash_albert",
            "timezoneOffset": -330,
            "language": "en-IN"
        },
        "behavioral_data": {
            "hold_mean": 90, "hold_std": 10,
            "iki_mean": 150, "iki_std": 20,
            "backspace_count": 0, "hesitation_ms": 100,
            "mouse_entropy": 5, "gyro_angle": 45,
            "transaction_amount": 2500.0
        }
    }, headers={"Authorization": f"Bearer {albert_token}"})
    
    # Expected: Allowed
    print(f"Status Code: {resp.status_code}")
    data = resp.json()
    print(f"Action: {data.get('action')}")
    print("Reasons:")
    for r in data.get("reasons", []):
        print(f"  -> {r}")

    # Scenario 3: Albert's credentials stolen
    print("\n--------------------------------------------------")
    print("[SCENARIO 3] Albert's credentials stolen (high-value attack)")
    print("Attacker tries Rs. 20000 to unknown UPI")
    print("--------------------------------------------------")
    time.sleep(1)
    
    resp = requests.post(f"{BASE_URL}/transaction", json={
        "username": "albert@upi",
        "payee_upi": "unknown88@upi",
        "amount": 20000.0,
        "device": {
            "userAgent": "Samsung S23",
            "screenRes": "1080x2340",
            "canvasHash": "mock_hash_albert",
            "timezoneOffset": -330,
            "language": "en-IN"
        },
        "behavioral_data": {
            "hold_mean": 90, "hold_std": 10,
            "iki_mean": 150, "iki_std": 20,
            "backspace_count": 0, "hesitation_ms": 100,
            "mouse_entropy": 5, "gyro_angle": 45,
            "transaction_amount": 20000.0
        }
    }, headers={"Authorization": f"Bearer {albert_token}"})
    
    # Expected: Blocked or OTP Challenge
    print(f"Status Code: {resp.status_code}")
    data = resp.json()
    print(f"Action: {data.get('action')}")
    print("Reasons:")
    for r in data.get("reasons", []):
        print(f"  -> {r}")
        
    print("\n==================================================")
    print("DEMO COMPLETE. Check terminal output of backend for colored logs.")
    print("==================================================")

if __name__ == "__main__":
    simulate()
