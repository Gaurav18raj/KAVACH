import os
import subprocess
from pathlib import Path

# Base directory
base_dir = Path("E:/Self Project/Kavach")
base_dir.mkdir(parents=True, exist_ok=True)

# List of files to create
files = [
    "README.md",
    "docker-compose.yml",
    ".env.example",
    "requirements.txt",
    "android-app/app/src/main/java/com/kavach/ui/auth/LoginActivity.kt",
    "android-app/app/src/main/java/com/kavach/ui/auth/RegistrationActivity.kt",
    "android-app/app/src/main/java/com/kavach/ui/dashboard/DashboardActivity.kt",
    "android-app/app/src/main/java/com/kavach/sensors/KeystrokeDynamics.kt",
    "android-app/app/src/main/java/com/kavach/sensors/HapticNavigationTracker.kt",
    "android-app/app/src/main/java/com/kavach/sensors/IMUSensor.kt",
    "android-app/app/src/main/java/com/kavach/sensors/DeviceIntelligenceCollector.kt",
    "android-app/app/src/main/java/com/kavach/sensors/SensorEventBundler.kt",
    "android-app/app/src/main/java/com/kavach/enrollment/EnrollmentManager.kt",
    "android-app/app/src/main/java/com/kavach/enrollment/PhaseDetector.kt",
    "android-app/app/src/main/java/com/kavach/network/ApiClient.kt",
    "android-app/app/src/main/java/com/kavach/network/BehavioralEventPayload.kt",
    "backend/gateway/app.py",
    "backend/gateway/middleware/jwt_validator.py",
    "backend/gateway/middleware/rate_limiter.py",
    "backend/gateway/middleware/pii_stripper.py",
    "backend/gateway/nginx/nginx.conf",
    "backend/risk_engine/app.py",
    "backend/risk_engine/composite_scorer.py",
    "backend/risk_engine/sub_scorers/behavioral.py",
    "backend/risk_engine/sub_scorers/device.py",
    "backend/risk_engine/sub_scorers/context.py",
    "backend/risk_engine/sub_scorers/failed_login.py",
    "backend/risk_engine/response_protocol.py",
    "backend/risk_engine/enrollment_fallback.py",
    "backend/risk_engine/schemas/risk_payload.py",
    "backend/ml_engine/models/isolation_forest/model.py",
    "backend/ml_engine/models/isolation_forest/trainer.py",
    "backend/ml_engine/models/isolation_forest/predictor.py",
    "backend/ml_engine/models/one_class_svm/model.py",
    "backend/ml_engine/models/one_class_svm/predictor.py",
    "backend/ml_engine/models/lstm_nav/model.py",
    "backend/ml_engine/models/lstm_nav/trainer.py",
    "backend/ml_engine/models/lstm_nav/predictor.py",
    "backend/ml_engine/models/lstm_nav/screen_tokenizer.py",
    "backend/ml_engine/models/device_validator/jaccard_matcher.py",
    "backend/ml_engine/models/device_validator/emulator_flags.py",
    "backend/ml_engine/models/device_validator/vpn_ip_checker.py",
    "backend/ml_engine/xai/shap_explainer.py",
    "backend/ml_engine/xai/nl_reason_mapper.py",
    "backend/ml_engine/enrollment/enrollment_manager.py",
    "backend/ml_engine/enrollment/baseline_builder.py",
    "backend/ml_engine/enrollment/phase_detector.py",
    "backend/ml_engine/continuous_auth/rolling_scorer.py",
    "backend/ml_engine/continuous_auth/transaction_gate.py",
    "backend/ml_engine/features/keystroke_extractor.py",
    "backend/ml_engine/features/haptic_extractor.py",
    "backend/ml_engine/features/imu_extractor.py",
    "backend/ml_engine/features/context_extractor.py",
    "backend/audit/kafka_producer.py",
    "backend/audit/es_sink.py",
    "backend/audit/rbi_report_generator.py",
    "backend/db/postgres/models.py",
    "backend/db/postgres/migrations/001_initial.sql",
    "backend/db/mongo/behavioral_events.py",
    "backend/db/redis_client.py",
    "backend/db/elastic/audit_index.py",
    "notebooks/01_keystroke_eda.ipynb",
    "notebooks/02_isolation_forest_tuning.ipynb",
    "notebooks/03_lstm_nav_sequence.ipynb",
    "notebooks/04_shap_explanation.ipynb",
    "notebooks/05_far_frr_analysis.ipynb",
    "datasets/README.md",
    "infra/Dockerfile.gateway",
    "infra/Dockerfile.risk_engine",
    "infra/Dockerfile.ml_engine",
    "infra/k8s/deployment.yaml",
    "infra/k8s/hpa.yaml",
    "tests/test_composite_scorer.py",
    "tests/test_keystroke_features.py",
    "tests/test_device_validator.py",
    "tests/test_enrollment_phase.py",
    "tests/test_continuous_auth.py",
    "tests/test_adversarial_replay.py"
]

print("Creating folder structure...")
for f in files:
    path = base_dir / f
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.touch()

# Details MD files
docs_dir = base_dir / "docs"
docs_dir.mkdir(parents=True, exist_ok=True)

docs = {
    "1_Honest_Assessment.md": """# 1. Honest Assessment

| Dimension | Score | Verdict |
|-----------|-------|---------|
| Innovation | 7/10 | Good signal combination; IF + LSTM is not novel alone |
| Feasibility | 6/10 | High implementation complexity; needs scoping |
| Impact | 9/10 | Directly addresses RBI 2021 mandate + rising UPI fraud |
| Research Grounding | 5/10 | Needs explicit paper citations for judge credibility |
| Demo-Readiness | 6/10 | Too many moving parts; need a clear MVP path |
""",

    "2_Critical_Gaps.md": """# 2. Critical Gaps (Honest, Fix These First)

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
Everything else (bank details) → conceptual mention only. Keep your demo focused on **behavioral auth**, not KYC.
""",

    "3_Architecture_Enhancements.md": """# 3. Architecture Enhancements (Research-Grounded)

### Enhancement A — Behavioral DNA Profile (Privacy Innovation)
Instead of storing raw keystroke sequences, store **statistical moments**:
```python
# baseline_builder.py
behavioral_dna = {
    "hold_mean": np.mean(hold_durations),
    "hold_std":  np.std(hold_durations),
    "hold_skew": scipy.stats.skew(hold_durations),
    "iki_mean":  np.mean(inter_key_intervals),
    "iki_std":   np.std(inter_key_intervals),
    "swipe_velocity_p50": np.percentile(swipe_velocities, 50),
    "touch_pressure_mean": np.mean(touch_pressures),
}
```
**Why:** Cannot reconstruct raw keystrokes from statistical moments → RBI data minimization compliant. **Strong judge angle: privacy-by-design**.

### Enhancement B — One-Class SVM Fallback During Enrollment
During enrollment phase (sessions 1–5), Isolation Forest has insufficient data.  
Use **One-Class SVM** (works on small N) as interim scorer:
```python
from sklearn.svm import OneClassSVM
# Train on first 3 sessions (as few as 30 samples)
oc_svm = OneClassSVM(kernel='rbf', nu=0.05)
```
Switch to Isolation Forest after session 5. This ensures **zero gap** in anomaly detection.

Reference: *One-Class SVM for behavioral biometrics (Mahbub et al., 2016)* — works well on sparse enrollment data.

### Enhancement C — IMU Fusion (Mobile-Specific Differentiator)
Add accelerometer + gyroscope signals during typing:
```kotlin
// KeystrokeSensor.kt — add alongside existing signals
sensorManager.registerListener(this, accel, SensorManager.SENSOR_DELAY_GAME)
sensorManager.registerListener(this, gyro, SensorManager.SENSOR_DELAY_GAME)

// Capture: phone tilt angle, micro-tremor pattern during typing
```
**Why this matters:** Every person holds a phone slightly differently. Gyroscope captures unique hand tremor signature — very hard to spoof. Referenced in *"TouchBio" (Meng et al., 2015)*.

### Enhancement D — Cross-Channel Behavioral Consistency
The problem statement covers **Internet Banking + Mobile + UPI**. Your behavioral profile should be channel-aware:
```
same user, different channels → behavioral features differ
Channel-specific baselines:
  - mobile_behavioral_baseline
  - web_behavioral_baseline (mouse dynamics + typing cadence)
  - upi_behavioral_baseline (UPI PIN + app navigation)
```
Store `channel_type` enum in PostgreSQL. Isolation Forest models are **per-user × per-channel**.

### Enhancement E — Failed Login Behavioral Profiling
Problem statement: *"Harden login process after unsuccessful login attempts"*  
Current plan: No specific handling.  
**Fix:**
```python
# On failed login attempt:
failed_attempt_vector = extract_features(failed_event)
# Is the typing pattern consistent with the real user?
# → Real user mistyped their MPIN → FRR event, reduce weight
# → Unknown typing pattern → likely attacker probing
# → 3 consecutive unknown-pattern failures → lock + alert

# Exponential backoff: 1st fail → 30s wait, 2nd → 2min, 3rd → 10min
```
Flag: if failed attempt behavioral signature **differs significantly** from user baseline → elevate to HIGH risk immediately.
""",

    "4_Revised_Risk_Formula.md": """# 4. Revised Risk Formula

```
Current:  Risk = 0.45×Behavioral + 0.30×Device + 0.25×Context

Improved: Risk = 0.40×Behavioral + 0.25×Device + 0.20×Context + 0.15×FailedLoginBehavior
```
During enrollment phase (no ML):
```
Risk = 0.70×Device + 0.30×Context  (rule-based fallback)
```
""",

    "5_End_to_End_Workflow.md": """# 5. End-to-End Workflow

### Phase A — Registration + Enrollment
```
User Installs App
    │
    ├── Registers: name, user_id, password, MPIN, mobile, DOB
    │   └── password_validator.py → checks 12+ chars, no series (123/456), no name match
    │
    └── Enrollment Phase (Sessions 1–5)
            ├── SensorEventBundler captures all signals silently
            ├── NO Isolation Forest scoring (insufficient data)
            ├── Risk = 0.70×Device + 0.30×Context (rule-based)
            ├── baseline_builder.py accumulates behavioral_dna stats
            └── After session 5 → enrollment_phase = FALSE
                └── Isolation Forest trained on first 30 events
                    → Production mode activated
```

### Phase B — Normal Login (Production Mode)
```
User opens app → Layer 2 sensors activate silently
    │
    ├── User types User ID + MPIN
    │   └── KeystrokeDynamics.kt: hold_ms[], IKI[], commit_hesitation_ms
    │   └── IMUSensor.kt: phone_tilt[], micro_tremor[]
    │
    ├── SensorEventBundler packages payload
    │
    ├── → Auth Gateway (FastAPI + NGINX)
    │       ├── JWT validated
    │       ├── Rate limit: 100/min (Redis)
    │       └── PII stripped (GPS raw, account_no removed)
    │
    ├── → Risk Scoring Engine
    │       ├── behavioral_scorer.py → Isolation Forest → score ∈ [0,1]
    │       ├── device_scorer.py → Jaccard fingerprint match
    │       ├── context_scorer.py → impossible_travel, time_anomaly
    │       └── composite_scorer.py → 0.40B + 0.25D + 0.20C + 0.15F
    │
    ├── → XAI Layer
    │       └── SHAP values → natural language reason strings
    │
    └── → Response Protocol (Layer 6)
            ├── < 0.25: proceed normally
            ├── 0.25–0.50: OTP to registered mobile
            ├── 0.50–0.72: biometric challenge (Face ID / Fingerprint)
            └── > 0.72: session blocked + fraud desk webhook
```

### Phase C — Continuous Authentication During Session
```
Session Active (user on dashboard / performing transactions)
    │
    ├── HapticNavigationTracker.kt streams live:
    │   swipe_pattern, nav_sequence[], inactivity_gaps, screen_timing
    │
    ├── Every 30 seconds:
    │   └── rolling_scorer.py re-evaluates using cached session signals (Redis)
    │       └── If risk delta > 0.15 from login score → re-challenge
    │
    └── On high-value actions (Send Money / Bank Transfer):
            └── transaction_gate.py forces fresh composite score
                └── If score > 0.50 → block transaction → step-up auth
```

### Phase D — Model Maintenance
```
Background (Celery / Cron):
    ├── Every 7 days or 50 new clean sessions:
    │   └── trainer.py → incremental Isolation Forest retrain per user
    │
    ├── Daily:
    │   └── MongoDB TTL index purges events older than 90 days
    │
    └── On CRITICAL flag:
        └── Kafka → Elasticsearch → fraud officer dashboard
            └── SHAP reason + full session audit trail available
```
""",

    "6_ML_Model_Refinements.md": """# 6. ML Model Refinements

### Isolation Forest — Parameter Guidance
```python
from sklearn.ensemble import IsolationForest

# Per-user model
model = IsolationForest(
    n_estimators=100,
    max_samples='auto',
    contamination=0.05,   # Assume 5% anomalous sessions
    random_state=42
)

# Feature vector per session (17 features):
features = [
    hold_mean, hold_std, hold_skew,         # Keystroke
    iki_mean, iki_std,                       # Inter-key interval
    backspace_count, backspace_position_avg, # Error pattern
    commit_hesitation_ms,                    # Final send hesitation
    swipe_velocity_p50, touch_pressure_mean, # Haptic
    nav_sequence_len, session_duration_s,    # Navigation
    phone_tilt_mean, micro_tremor_std,       # IMU (NEW)
    time_since_last_login_h,                 # Temporal
    login_hour_of_day,                       # Time pattern
    geo_zone_match                           # Context
]
```

### LSTM Nav Sequence
```python
# Screen tokens (example)
SCREEN_MAP = {
    "login": 0, "dashboard": 1, "send_money": 2,
    "confirm": 3, "upi_pin": 4, "success": 5,
    "recharge": 6, "bank_transfer": 7
}

# Model: predicts next screen from sequence of past screens
# Anomaly: if predicted confidence for actual next screen < 0.3 → contextual risk elevated
```

### SHAP → Natural Language (for RBI Audit Panel)
```python
REASON_TEMPLATES = {
    "hold_mean": "Typing speed unusually {direction} compared to baseline",
    "commit_hesitation_ms": "User hesitated {duration}ms before confirming — {direction} than normal",
    "geo_zone_match": "Login location inconsistent with registered region",
    "phone_tilt_mean": "Device held at unusual angle during PIN entry",
    "impossible_travel": "Login from {city} — {km}km from last known location in {hours}h",
}
```
""",

    "7_Research_References.md": """# 7. Research & Dataset References

## Research References

| Paper | Relevance |
|-------|-----------|
| Acien et al. (2022). *"TypeNet: Deep Learning Keystroke Biometrics."* IEEE TBIOM | Validates keystroke deep learning; minimum sample requirements |
| Frank et al. (2013). *"Touchalytics: On the Applicability of Touchscreen Input as a Behavioral Biometric."* IEEE TIFS | Foundational continuous auth via touch — directly validates your haptic layer |
| Liu et al. (2008). *"Isolation Forest."* IEEE ICDM | Your primary anomaly detection algorithm — cite methodology directly |
| Meng et al. (2015). *"Surveying the Development of Biometric User Authentication on Mobile Phones."* IEEE CST | Validates IMU fusion + swipe biometrics on mobile |
| Killourhy & Maxion (2009). *"Comparing Anomaly-Detection Algorithms for Keystroke Dynamics."* DSN | CMU Keystroke dataset — use for baseline evaluation + FAR/FRR |
| RBI (2021). *"Master Direction on Digital Payment Security Controls"* | Regulatory grounding — cite for RBI compliance requirement of behavioral controls |
| NPCI UPI Security Guidelines (2022) | UPI-specific behavioral auth requirements |

## Dataset References

| Dataset | Use Case | Link |
|---------|----------|------|
| CMU Keystroke Dynamics Benchmark | FAR/FRR baseline eval, 51 users | cs.cmu.edu/~keystroke |
| GREYC Keystroke Dataset | Multi-session keystroke patterns | epaymentbiometrics.ensicaen.fr |
| MotionSense (Malekzadeh et al.) | IMU / accelerometer behavioral data | GitHub: MotionSense |
| UMDAA-02 | Mobile touch + IMU continuous auth | Univ. of Maryland |
""",

    "8_MVP_and_Criteria.md": """# 8. MVP Scope & Judging Criteria Alignment

## MVP Scope

| Priority | Feature | Effort |
|----------|---------|--------|
| **MUST HAVE** | Login with keystroke capture + Isolation Forest scoring | Medium |
| **MUST HAVE** | Device fingerprint validator (Jaccard) | Low |
| **MUST HAVE** | Response protocol (4 tiers) | Low |
| **MUST HAVE** | Enrollment phase (5-session gate) | Low |
| **MUST HAVE** | SHAP-based audit reason string | Medium |
| **GOOD TO HAVE** | LSTM navigation sequence model | High |
| **GOOD TO HAVE** | Continuous auth during session | Medium |
| **GOOD TO HAVE** | IMU fusion (accelerometer + gyro) | Medium |
| **GOOD TO HAVE** | FAR/FRR evaluation notebook | Low |
| **FUTURE SCOPE** | Federated learning across banks | Very High |
| **FUTURE SCOPE** | Cross-channel behavioral consistency (web + mobile + UPI) | High |
| **FUTURE SCOPE** | Voice biometrics for high-value transactions | High |

## Judging Criteria Alignment

| Problem Statement Goal | Your Coverage | Status |
|------------------------|---------------|--------|
| Differentiate legitimate vs suspicious users | Composite risk score + 4-tier response | ✅ Strong |
| Identify behavioral patterns at login | Keystroke dynamics + haptic capture | ✅ Strong |
| AI-enabled behavior-based auth | Isolation Forest + LSTM + Device Validator | ✅ Strong |
| Harden login after unsuccessful attempts | Failed login behavioral profiling + backoff | ⚠️ Add explicitly |
| Behavior-based risk scoring | Composite formula with weights | ✅ Strong |
| Prevent account takeover | Continuous auth + session-level scoring | ⚠️ Add explicitly |
| Multi-channel (Internet + Mobile + UPI) | Channel-specific baselines | ⚠️ Mention in architecture |

**What judges will like:**
- Behavioral DNA (privacy-preserving statistical profile) — novel framing
- SHAP explainability for RBI audit — directly tied to regulation
- Enrollment phase handling — shows you thought about real-world deployment
- Composite risk formula with tunable weights — bank-configurable

**What judges may penalize:**
- No FAR/FRR numbers cited → looks unvalidated
- Over-complex registration form → confused focus
- MPIN sparsity not addressed → technical weakness if questioned
- No mention of adversarial attacks (replay, behavioral spoofing) → security gap
"""
}

print("Creating docs...")
for doc_name, content in docs.items():
    with open(docs_dir / doc_name, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\\n")

# Main README.md
readme_content = """# KAVACH — Enhanced Behavioral Authentication Plan
> Hackathon Strategy Document | AI-Driven Behavioral Authentication for Digital Banking

This repository contains the architecture, planning, and structural components for the KAVACH Behavioral Authentication project.

## Key Features

1. **Behavioral DNA Profile** - Privacy-preserving statistical fingerprint.
2. **Cold Start Protocol** - Safely manages the first 5 sessions before enabling ML scoring.
3. **Continuous Authentication** - Validates session integrity every 30s and prior to major transactions.
4. **IMU Fusion** - Utilizes accelerometer and gyroscope signatures against behavioral spoofing.

## Documentation Overview

Refer to the `/docs` directory for full architectural plans:
- [Honest Assessment](docs/1_Honest_Assessment.md)
- [Critical Gaps & Fixes](docs/2_Critical_Gaps.md)
- [Architecture Enhancements](docs/3_Architecture_Enhancements.md)
- [Revised Risk Formula](docs/4_Revised_Risk_Formula.md)
- [End-to-End Workflow](docs/5_End_to_End_Workflow.md)
- [ML Model Refinements](docs/6_ML_Model_Refinements.md)
- [Research & Datasets](docs/7_Research_References.md)
- [MVP Scope & Judging Criteria Alignment](docs/8_MVP_and_Criteria.md)

## Unique Innovation

**Behavioral DNA Hashing**: Unlike existing systems that store raw biometric data, Kavach computes a statistical behavioral fingerprint (mean, standard deviation, skewness of each signal modality) that cannot be reverse-engineered into the original biometric data. This privacy-preserving design aligns with RBI's data minimization requirements while maintaining authentication accuracy.
"""
with open(base_dir / "README.md", "w", encoding="utf-8") as f:
    f.write(readme_content.strip() + "\\n")

print("Initializing git repository...")
try:
    subprocess.run(["git", "init"], cwd=base_dir, check=True)
    subprocess.run(["git", "add", "."], cwd=base_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit: Scaffold KAVACH Behavioral Authentication architecture and documentation"], cwd=base_dir, check=True)
    print("Git repository initialized successfully.")
except Exception as e:
    print(f"Error initializing git: {e}")

print("Done! Folder structure, details md files, and github ready.")
