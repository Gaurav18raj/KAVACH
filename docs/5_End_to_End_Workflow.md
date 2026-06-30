# 5. End-to-End Workflow

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
```\n