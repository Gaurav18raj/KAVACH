# 6. ML Model Refinements

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
```\n