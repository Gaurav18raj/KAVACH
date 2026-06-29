# KAVACH System Architecture & Deep Dive

This document serves as the technical blueprint for the **KAVACH Behavioral Authentication Engine**. It details the structural logic, data flow, ML algorithms, and the integration pathways necessary for scaling this into enterprise banking systems.

## 1. Core Philosophy

Traditional authentication relies on static credentials—passwords, PINs, or SMS OTPs. These are binary: you either have the credential or you don't. In the era of social engineering and screen-sharing attacks, static credentials are no longer sufficient. 

**Kavach shifts the paradigm from "What you know" to "How you behave".** It continuously analyzes the *human* on the other end of the screen without interrupting their banking experience.

## 2. The Sensor Fusion Pipeline

Kavach does not rely on a single data point. It fuses three distinct vectors of telemetry:

### A. Behavioral Biometrics (The "How")
- **Hold Mean & StdDev:** The average time a user holds down a key.
- **Inter-Key Interval (IKI):** The rhythm or delay between successive keystrokes.
- *Why it matters:* A fraudster operating via AnyDesk or reading a stolen password from a notepad types with entirely different physical cadence than the actual account holder.

### B. Device & Haptic Entropy (The "Where")
- **Mouse Entropy:** Calculates the variance and jerkiness of pointer movements. High entropy strongly correlates with the network latency introduced by remote desktop software (TeamViewer, AnyDesk).
- **Gyroscope Pitch/Roll:** In mobile environments, legitimate users naturally tilt and micro-shift their phones. If the gyro returns a perfect `0.0` over a long duration, it flags a potential automated bot or an emulator.

### C. Kavach Ledger Intelligence (KLI) (The "What")
- Analyzes the context of the transaction itself. 
- *Why it matters:* If user "Deepak" has a 30-day average transaction size of ₹500 (groceries, tea), a sudden ₹90,000 transfer at 2 AM is highly anomalous. Conversely, for user "Albert" whose daily average is ₹3,000, a ₹5,000 transfer might be completely benign. KLI contextualizes the risk based on the individual's *financial DNA*.

## 3. Data Flow & Execution Diagram

Below is the execution flow from the moment the user clicks "Send Money" to the final banking core authorization:

```text
[Frontend Browser / App]
       │
       ├─> User enters details & MPIN
       ├─> Kavach Edge SDK invisibly records: 
       │     (Keystrokes, Mouse Entropy, Gyroscope, Canvas Hash)
       │
       ▼
[POST /api/v1/transaction]
       │
       ├──> 1. Authentication Layer (Validates JWT & MPIN)
       │
       ├──> 2. Behavioral Scorer (Phase 1 ML)
       │       - Computes Z-Scores against historical DNA
       │       - Flags AnyDesk/Bot anomalies
       │
       ├──> 3. KLI Transaction Scorer
       │       - Checks Amount Deviation against historical average
       │       - Checks Recipient Trust (New vs Saved Payee)
       │       - Checks Velocity (Rapid successive transfers)
       │
       ▼
[Composite Risk Engine]
       │
       ├──> Final Risk Score = (0.55 * KLI) + (0.45 * Behavioral)
       │
       ├──> If Score < 0.25 (Safe) ─────────> Returns HTTP 200 (Execute Txn)
       ├──> If Score 0.25 - 0.75 (Warn) ────> Returns OTP_CHALLENGE
       └──> If Score > 0.75 (Critical) ─────> Returns BLOCK & Alert Fraud Team
```

## 4. Machine Learning Implementation

In its current prototype phase, Kavach utilizes Statistical Machine Learning designed for extremely low latency (< 15ms inference time).

**Algorithm:** Z-Score Anomaly Detection
$$ Z = \frac{|X - \mu|}{\sigma} $$
Where $X$ is the current payload (e.g., typing hold time), $\mu$ is the baseline mean, and $\sigma$ is the baseline standard deviation.
We use a Sigmoid function to normalize the infinite Z-Score into a bounded $0 \dots 1$ risk probability.

## 5. Future Goal: Enterprise Banking Integration

To integrate Kavach natively into an enterprise bank's architecture (like Central Bank of India), the following upgrades are planned:

1. **LightGBM / XGBoost:** Transition from statistical Z-Scores to Gradient Boosted Trees for the Transaction Scorer, offering higher accuracy on highly imbalanced fraud datasets.
2. **Federated Learning for Privacy:** Banks cannot legally store plaintext keystrokes. Kavach SDK will run a lightweight TensorFlow.js model directly on the client's device, transmitting only encrypted, aggregated risk vectors to the server.
3. **FIDO2 Passkeys:** If Kavach flags a medium-risk anomaly, instead of relying on an SMS OTP (which can be intercepted by malware), Kavach will trigger a WebAuthn Biometric prompt (FaceID/TouchID) to definitively verify the human.
