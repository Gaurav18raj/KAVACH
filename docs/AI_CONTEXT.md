# KAVACH - Universal AI System Context
**INSTRUCTION FOR LLMs:** If you are reading this file, use it as the absolute ground truth for the KAVACH architecture, problem statement, business logic, and technical stack. This document is designed to give you instant, deep context so you do not hallucinate file structures or project goals.

---

## 1. Problem Statement & Goal
- **The Problem:** Digital banking fraud in India (UPI/IMPS) is evolving. Fraudsters use social engineering (Jamtara scams) or Remote Desktop apps (AnyDesk, TeamViewer) to steal credentials or hijack active sessions. Once logged in, traditional banks assume the session is legitimate because the correct Password/OTP was provided.
- **The Goal:** Build an AI-driven, Zero-Trust Behavioral Authentication system that validates *who* is behind the keyboard continuously. Differentiate between a legitimate user and a hacker/bot *during* the session without adding friction (e.g., constant OTPs) for normal behavior.
- **Core Value Proposition:** Authenticate the human, not just the credential. Prevent Account Takeover (ATO) and implement behavior-based risk scoring.

## 2. Technical Stack & File Structure
- **Backend Framework:** Python 3.9+, FastAPI, SQLAlchemy (SQLite for demo).
- **Frontend:** Vanilla HTML/CSS/JS (Zero framework dependencies to ensure ultra-low latency).
- **ML Paradigm:** Statistical Machine Learning (Z-Scores, Welford's Algorithm) optimized for <15ms Edge/Backend inference. Do *not* suggest heavy models like PyTorch/TensorFlow for the current MVP.
- **Key Directories:**
  - `backend/main.py`: The FastAPI router and API gateway. Also contains Custom Logging Middleware to output interactive UI actions to the terminal.
  - `backend/risk_engine/`: Contains `behavioral_scorer.py`, `transaction_scorer.py`, and `composite_scorer.py` (The ML brain).
  - `backend/models.py` & `schemas.py`: SQLAlchemy database models (`User`, `UserDNA`, `TransactionHistory`) and Pydantic validation schemas.
  - `frontend/js/kavach-sdk.js`: The silent Edge Data Collector running in the browser.
  - `start_kavach.py`: The root CLI orchestrator and menu for launching the server or tests.

## 3. The 3-Pillar Sensor Fusion Architecture
Kavach does not rely on one signal. It computes a unified Risk Score (0.0 to 1.0) by fusing three independent data vectors via `composite_scorer.py` (Formula: `0.55 * Financial Risk + 0.45 * Behavioral Risk`):

1. **Behavioral Biometrics (Keystroke Dynamics):**
   - *Metrics:* Hold Time (ms key is pressed) and Inter-Key Interval (IKI, ms between keys).
   - *Logic:* Handled by `behavioral_scorer.py`. Uses Z-Scores ($Z = |X - \mu| / \sigma$) to check if the current typing rhythm deviates significantly from the user's historical `UserDNA`.
2. **Device & Haptic Entropy (Sensor Fusion):**
   - *Metrics:* Mouse Movement Entropy (Variance/Speed) and Gyroscope Pitch.
   - *Logic:* High mouse entropy flags Remote Desktop network latency (AnyDesk stuttering). A perfectly flat gyroscope (0.0) on a mobile device flags an automated bot or emulator.
3. **Kavach Ledger Intelligence (KLI - Financial Context):**
   - *Metrics:* 30-day moving average of transaction amounts, Payee trust, and Velocity.
   - *Logic:* Handled by `transaction_scorer.py`. Contrast logic ("Deepak vs Albert"). If Deepak normally spends ₹500/day, a ₹90,000 transfer is blocked. If Albert averages ₹3000/day, a ₹5,000 transfer is allowed.

## 4. API & Data Flow Execution
1. **Client Interaction:** User fills out the transfer form on `frontend/send-money.html`.
2. **Edge Collection:** `kavach-sdk.js` captures keystrokes, calculates hesitation, mouse entropy, and fetches the `canvasHash` from `localStorage`.
3. **API Request:** Frontend calls `POST /api/v1/transaction` with the transaction details and the SDK `behavioral_data`.
4. **Backend Processing:** `main.py` routes the request to the `composite_scorer.calculate_composite_risk()`.
5. **Decision:** The engine returns `access_granted` (True/False), a `risk_level` (`SAFE`, `CHALLENGE`, `CRITICAL`), and human-readable `reasons`.
6. **UI Feedback:** The frontend dynamically renders a Green (Allowed) or Red (Blocked) Kavach Risk Banner.

## 5. Critical Technical Constraints & Rules
If you are generating code or modifying this repository, obey these rules:
- **FastAPI Static Route Shadowing:** In `backend/main.py`, the frontend is served via `app.mount("/", StaticFiles(directory=FRONTEND_DIR))`. Because FastAPI evaluates top-down, **all API routes (`@app.get("/api/v1/...")`) MUST be placed above the `app.mount` line.**
- **No Heavy Deep Learning:** The current architecture mandates high-speed statistical logic. Do not implement heavy Deep Learning models without explicit permission.
- **Data Privacy (RBI Compliance):** Kavach does *not* log or store raw plaintext passwords, usernames in URLs, or literal keys pressed. We only store aggregate mathematical vectors (mean, std).
- **Interactive Terminal:** `main.py` includes a `@app.middleware("http")` function that uses `colorama`. It intercepts all UI actions to print a real-time matrix-style log to the CLI. Do not break or remove this middleware, as it is critical for the Hackathon Demo presentation.
- **Seed Data:** Do not require manual data entry to test. Use `seed_demo_data.py` to auto-populate the SQLite DB with baseline data for the KLI engine.
