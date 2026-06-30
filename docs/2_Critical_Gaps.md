# 2. Critical Gaps (Honest, Fix These First)

### GAP 1 — Cold Start / Enrollment Phase (CRITICAL)
**Problem:** New users have ZERO behavioral baseline. Your Isolation Forest has nothing to train on.  
**What happens now:** First 5–7 sessions → ML scoring would fire on empty data → false positives or crashes.  
**Fix:**
```
Registration → ENROLLMENT PHASE (sessions 1–5)
  ├── Silently collect behavioral events (no ML scoring yet)
  ├── Rule-based fallback only (device check + OTP)
  └── After 5 clean sessions → baseline established → ML scoring activates
```
Add `enrollment_phase` boolean to PostgreSQL `users` table. `phase_detector.py` gates ML calls.

### GAP 2 — MPIN Behavioral Sparsity
**Problem:** MPIN is 4–6 digits → gives only 4–6 hold duration values. Statistically weak for Isolation Forest.  
**Fix:** Do NOT rely on MPIN keystrokes alone. Fuse:
- Keystroke data from **MPIN + UPI PIN + search fields**  
- Haptic + IMU data during the **same session**  
- Swipe pressure during dashboard navigation  

Reference: *TypeNet (Acien et al., 2022)* trains on 15+ keystrokes minimum. Below that, accuracy drops sharply.

### GAP 3 — PII Contradiction
**Problem:** Layer 3 NGINX "strips PII" → but Layer 5 MongoDB stores raw `BehavioralEvent` documents.  
**Question:** What exactly is in those documents? Hold durations are fine. GPS coordinates are PII.  
**Fix:** Define a clear PII boundary:
```
PII (strip at gateway):     name, account_number, pan, aadhaar, gps_raw
Non-PII (safe to store):    hold_durations[], swipe_velocity, screen_sequence[], 
                             ip_city_hash, device_fp_hash, timezone_offset
```
Store only hashed/derived features in MongoDB. Raw GPS → store only `geo_zone_id` (North/South/East/West India grid).

### GAP 4 — No Continuous Authentication During Session
**Problem:** Your system only authenticates at **login**. A session-hijacking attack post-login goes undetected.  
**Fix:** Add rolling risk re-evaluation every 30 seconds or on each high-value action:
```
Session active →
  ├── Every 30s: re-compute composite score from live session signals
  ├── On "Send Money" / "Bank Transfer": mandatory re-score before execution  
  └── If score crosses threshold mid-session → step-up challenge injected
```
This is what separates **"login protection"** from **"continuous behavioral authentication"** — the latter is what the problem statement asks for.

### GAP 5 — No FAR/FRR/EER Targets Defined
**Problem:** Judges and bank security officers will ask: "What's your false acceptance rate?"  
**Fix:** Define targets upfront:
- **FAR (False Acceptance Rate):** Target < 2% (fraudster gets through)  
- **FRR (False Rejection Rate):** Target < 5% (legitimate user blocked)  
- **EER (Equal Error Rate):** Target < 3.5% (where FAR = FRR)  
- Evaluate against CMU Keystroke Benchmark dataset (free, labeled, 51 users)

### GAP 6 — Impossible Travel Not Properly Defined
**Problem:** Listed in Device Intelligence but never specified how it's computed.  
**Fix:**
```python
# PostgreSQL: users table
last_login_gps_lat, last_login_gps_lon, last_login_timestamp

# Logic in context_scorer.py
def check_impossible_travel(user_id, current_lat, current_lon, current_ts):
    prev = db.get_last_login(user_id)
    distance_km = haversine(prev.gps, current_gps)
    hours_elapsed = (current_ts - prev.ts).hours
    max_possible_speed = distance_km / hours_elapsed  # km/h
    if max_possible_speed > 900:  # faster than a commercial flight
        return ImpossibleTravelFlag(severity="HIGH", distance_km=distance_km)
```

### GAP 7 — Registration Form Scope Creep
**Problem:** Aadhaar + PAN + bank account + branch IFSC in one registration form is not behavioral auth — it's KYC. It adds no value to your demo.  
**Fix for demo:** Simplify registration to:
```
name, user_id, password, MPIN, mobile_number, DOB
```
Everything else (bank details) → conceptual mention only. Keep your demo focused on **behavioral auth**, not KYC.\n