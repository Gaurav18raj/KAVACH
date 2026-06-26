# 3. Architecture Enhancements (Research-Grounded)

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
Flag: if failed attempt behavioral signature **differs significantly** from user baseline → elevate to HIGH risk immediately.\n