import requests
import json
import time
import sys

# Force UTF-8 encoding for stdout just in case
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000/api/v1"

def print_result(scenario, r):
    print(f"\n{'='*50}\n[SCENARIO] {scenario}")
    try:
        data = r.json()
        print(f"Status Code: {r.status_code}")
        print(f"Access Granted: {data.get('access_granted')}")
        print(f"Risk Score: {data.get('risk_score')}")
        print(f"Action: {data.get('action')}")
        print("Reasons:")
        for reason in data.get('reasons', []):
            print(f"  -> {reason}")
    except:
        print(r.text)
    print('='*50)

# 1. Register a Good User
username = f"deepak_{int(time.time())}@upi"
print(f"\n[*] Registering New User: {username}")
requests.post(f"{BASE_URL}/register", json={
    "full_name": "Deepak Testing",
    "username": username,
    "password": "securepassword123"
})

good_device = {
    "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)",
    "screenRes": "390x844",
    "timezoneOffset": -330,
    "language": "en-IN",
    "canvasHash": "good_hash_iphone"
}

# 2. Phase 1 Enrollment (Good User, 5 Logins)
print("\n[*] Simulating 5 Legitimate Phase-1 Logins to build Baseline...")
for i in range(5):
    payload = {
        "username": username,
        "password": "securepassword123",
        "behavioral_data": {
            "hold_mean": 90.0, "hold_std": 10.0,
            "iki_mean": 150.0, "iki_std": 20.0,
            "backspace_count": 0, "hesitation_ms": 100.0,
            "mouse_entropy": 5.0, "gyro_angle": 45.0,
            "transaction_amount": 0.0 # Standard Login
        },
        "device": good_device
    }
    r = requests.post(f"{BASE_URL}/login", json=payload)
    if i == 0:
        print_result("Enrollment Login #1", r)

# 3. Phase 2 Production: Low Value UPI Transaction (Bypass ML)
payload["behavioral_data"]["transaction_amount"] = 500.0 # 500 INR
r = requests.post(f"{BASE_URL}/login", json=payload)
print_result("Production Phase - Low Value UPI (Rs.500) - Should Bypass ML", r)

# 4. Phase 2 Production: High Value RTGS (Good User)
payload["behavioral_data"]["transaction_amount"] = 65000.0 
r = requests.post(f"{BASE_URL}/login", json=payload)
print_result("Production Phase - High Value RTGS (Rs.65,000) - Good User", r)

# 5. Phase 2 Production: Hacker Attack (Jamtara AnyDesk Simulation)
# Hacker uses AnyDesk from a Windows PC, has high mouse entropy (latency), flat gyro, bad typing rhythm
hacker_device = {
    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 AnyDesk",
    "screenRes": "1920x1080",
    "timezoneOffset": -330,
    "language": "en-US",
    "canvasHash": "hacker_canvas_hash"
}
hacker_payload = {
    "username": username,
    "password": "securepassword123", # Hacker stole the password
    "behavioral_data": {
        "hold_mean": 250.0, "hold_std": 150.0, # Erratic, slow typing
        "iki_mean": 500.0, "iki_std": 300.0,
        "backspace_count": 5, "hesitation_ms": 2500.0,
        "mouse_entropy": 150.0, # High AnyDesk Latency
        "gyro_angle": 0.001,    # Phone lying perfectly flat
        "transaction_amount": 99000.0 # Trying to steal Rs.99,000
    },
    "device": hacker_device
}
r = requests.post(f"{BASE_URL}/login", json=hacker_payload)
print_result("Production Phase - Jamtara AnyDesk Hacker Attack (Rs.99,000)", r)
