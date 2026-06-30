# 8. MVP Scope & Judging Criteria Alignment

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
- No mention of adversarial attacks (replay, behavioral spoofing) → security gap\n