# KAVACH — Implementation Plan (PSB Hackathon Round 2 — Proof of Concept)

> **Target:** Working web demo showcasing AI-driven behavioral authentication for digital banking.  
> **Timeline:** Hackathon PoC — build fast, demo convincingly, impress judges.  
> **Medium:** Website first → App integration later.

---

## 🔴 Honest Assessment: Problems, Risks & Solutions

Before building, here are the real problems I see with the current plan and how to fix them:

### Problem 1: Scope is Too Large for a PoC Demo
> [!CAUTION]
> The plan describes ~65 new files, LSTM models, SHAP explainers, rolling scorers, and 8 dashboard actions. This is a **production system spec**, not a hackathon PoC. If you try to build all of it, nothing will work properly during demo.

**Solution:** Ruthlessly cut to a **Demo-Critical MVP** (see Phase 1 below). Build 3 flows end-to-end rather than 8 flows half-done.

### Problem 2: Real ML Models Need Real Data (You Don't Have Any)
> [!CAUTION]
> Isolation Forest needs 30+ behavioral sessions per user to train meaningfully. LSTM needs even more. At demo time, you'll have at most 2-3 test sessions. The model will produce garbage scores.

**Solution:**  
- **Phase 1 (Demo):** Use **rule-based scoring with statistical thresholds** (z-score from baseline). This is honest, works with minimal data, and is explainable.
- **Phase 2 (If time permits):** Add Isolation Forest as an optional backend that kicks in after enrollment. Pre-seed with synthetic behavioral data generated from your own typing patterns.
- **Alternative:** Pre-train on the **CMU Keystroke Dynamics Dataset** (51 users, 400 sessions each) and show the model works on research data, then demonstrate real-time capture on your demo app.

### Problem 3: LSTM Navigation Model Adds Zero Demo Value
> [!WARNING]
> The LSTM navigation prediction model adds massive complexity (PyTorch dependency, training loop, screen tokenization) but during a 10-15 minute demo, no judge will navigate enough pages to see it work.

**Solution:** **Drop LSTM entirely for PoC.** Replace with a simple **navigation sequence fingerprint** (ordered list comparison, Levenshtein distance). Document the LSTM as "Phase 3 — Production Roadmap."

### Problem 4: SHAP on Isolation Forest is Computationally Expensive
> [!WARNING]
> `shap.TreeExplainer` on sklearn's `IsolationForest` can take 2-5 seconds per prediction. During a live demo, this latency will kill the experience.

**Solution:** Pre-compute SHAP explanations for common patterns. For live demo, use a **reason mapping table** that maps which features deviate from baseline → human-readable strings. This gives the same explainability without the compute cost.

### Problem 5: No Actual Banking Backend
> [!IMPORTANT]
> This is a behavioral auth system, not a banking app. The mock banking flows (Send Money, Recharge, Bill Pay) need to look convincing but shouldn't have real transaction logic.

**Solution:** Mock all transactions with simulated success/failure. Focus demo time on the **behavioral scoring visualization** — show the risk score changing in real-time, show SHAP reasons, show the step-up challenge. That's what judges care about.

### Problem 6: Continuous Auth via Polling is Awkward
> [!NOTE]
> AJAX polling every 30s means 30s of delay before detecting suspicious behavior. In a demo, this feels sluggish.

**Solution:** Use **Server-Sent Events (SSE)** instead of polling. FastAPI supports SSE natively. Push risk score updates to the frontend in real-time. This looks dramatically better in demo.

### Problem 7: Indian Scenario Relevance Needs Explicit Mapping

**Solution:** Every demo screen should reference Indian-specific context:
- Use ₹ currency, Indian phone numbers (+91), UPI IDs (user@upi)
- Reference RBI Master Direction 2021 in the security dashboard
- Show UPI-style PIN entry (not generic password)
- Use Indian bank names and IFSC codes in mock transfers
- Show "Digital Rupee" awareness in future roadmap

---

## What You Actually Need (Technical Requirements)

### Must Have for Demo Day
| # | Requirement | Why |
|---|-------------|-----|
| 1 | **Working registration flow** | Shows enrollment phase concept |
| 2 | **Login with real keystroke capture** | Core behavioral biometric — this IS the product |
| 3 | **Real-time risk score display** | Visual proof that the system works |
| 4 | **Risk level response** (Allow/OTP/Block) | Shows the security decision engine |
| 5 | **Device fingerprinting** | Shows multi-signal approach |
| 6 | **Explainable AI reasons** | "Why was this flagged?" — judges love this |
| 7 | **Audit trail view** | Shows compliance readiness (RBI) |
| 8 | **Side-by-side demo** (real user vs impersonator) | The money shot — proves the system works |

### Nice to Have
| # | Requirement | Why |
|---|-------------|-----|
| 9 | Continuous auth during session | Shows it's not just login-time |
| 10 | Failed login behavioral profiling | Shows attacker detection |
| 11 | MPIN entry behavioral capture | Shows UPI-specific capability |
| 12 | Multi-device comparison | Shows cross-channel applicability |

### Drop for PoC (Document as Roadmap)
| # | Requirement | Why Drop |
|---|-------------|----------|
| 13 | LSTM navigation model | Too complex, no demo data |
| 14 | Federated learning | Phase 3 concept |
| 15 | Docker deployment | Judges won't check infrastructure |
| 16 | Full test suite | PoC, not production |
| 17 | Bill Pay, Recharge flows | 2-3 flows sufficient to demonstrate |

---

## Technical Workflow (How It Actually Works)

### The Demo Flow (What Judges Will See)

```
┌─────────────────────────────────────────────────────────────┐
│                    DEMO SCENARIO 1                          │
│              "Legitimate User Login"                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Open KAVACH Banking Portal (premium dark UI)            │
│  2. Type username slowly, naturally                         │
│  3. Type password with normal rhythm                        │
│  4. System captures: keystroke timing, device fingerprint   │
│  5. Risk Score: 0.12 (LOW) → ✅ Access Granted             │
│  6. Show real-time score breakdown on dashboard             │
│  7. Navigate to "Send Money" → score stays low              │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    DEMO SCENARIO 2                          │
│              "Attacker/Impersonator"                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Same credentials, DIFFERENT person typing               │
│  2. Different typing rhythm, speed, error pattern           │
│  3. Different device fingerprint (or incognito)             │
│  4. Risk Score: 0.68 (HIGH) → 🔒 Step-Up Auth Required     │
│  5. Show SHAP reasons: "Typing speed 2.3x faster than      │
│     baseline", "Unknown device", "Unusual login hour"       │
│  6. System blocks transaction, logs audit trail             │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    DEMO SCENARIO 3                          │
│              "Failed Login Attack"                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Wrong password attempts with suspicious typing          │
│  2. System detects: typing pattern ≠ real user              │
│  3. After 3 attempts → Account locked + Fraud alert         │
│  4. Show behavioral comparison chart                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Under-the-Hood Technical Flow

```
Browser (JavaScript SDK)                    Backend (Python/FastAPI)
━━━━━━━━━━━━━━━━━━━━━━━━━                  ━━━━━━━━━━━━━━━━━━━━━━━━
                                            
User types password                         
  │                                         
  ├─ keydown event → record timestamp       
  ├─ keyup event → calc hold_duration       
  ├─ inter-key interval (IKI) computed      
  ├─ backspace positions tracked            
  ├─ hesitation before submit detected      
  ├─ mouse movement entropy computed        
  ├─ device fingerprint generated           
  │   ├─ canvas hash                        
  │   ├─ WebGL renderer                     
  │   ├─ screen resolution                  
  │   ├─ timezone                           
  │   └─ user agent                         
  │                                         
  └─ Submit → POST /api/v1/login ─────────► Receive behavioral payload
     {                                        │
       username: "ramesh_kumar",              ├─ Validate JWT / credentials
       password: "****",                      ├─ Strip PII fields
       behavioral_data: {                     ├─ Extract features (17-dim vector)
         hold_durations: [82,95,71,...],       │   ├─ hold_mean, hold_std, hold_skew
         iki_values: [120,145,98,...],         │   ├─ iki_mean, iki_std
         backspace_count: 1,                  │   ├─ typing_speed_cps
         hesitation_ms: 340,                  │   ├─ backspace_ratio
         typing_speed: 5.2,                   │   └─ hesitation_ratio
         mouse_entropy: 3.7                   │
       },                                     ├─ Phase Detector
       device: {                              │   ├─ Enrollment? → Rule-based score
         fingerprint: "a7f3...",              │   └─ Production? → ML score
         timezone: "Asia/Kolkata",            │
         screen: "1920x1080",                 ├─ Risk Engine
         language: "en-IN"                    │   ├─ Behavioral: z-score from DNA
       }                                      │   ├─ Device: Jaccard similarity
     }                                        │   ├─ Context: time + location
                                              │   └─ Composite: weighted sum
                                              │
                                              ├─ XAI Reason Generator
                                              │   └─ "Typing 40% faster than usual"
                                              │
                                              └─ Response Decision
     ◄───────── Response ────────────────────    ├─ score: 0.12
     {                                           ├─ level: "LOW"
       risk_score: 0.12,                         ├─ action: "ALLOW"
       reasons: ["All signals normal"],
       session_token: "jwt..."
     }
```

---

## Phased Build Plan

### Phase 1: Foundation + Core Demo (Days 1-3) — MUST COMPLETE

#### Day 1: Project Setup + Frontend Shell
```
Tasks:
├── Initialize project structure (not all 65 files — just what's needed)
├── Create premium frontend UI
│   ├── Landing page with Kavach branding
│   ├── Login page with glassmorphism design
│   ├── Registration page
│   └── Dashboard (3 core actions: Send Money, Balance, History)
├── Implement kavach-sdk.js (keystroke capture module)
│   ├── Keystroke dynamics: hold_ms, IKI, backspace tracking
│   ├── Device fingerprinting: canvas, WebGL, UA, screen
│   └── Event bundler: packages all data into JSON
└── Test: Verify console.log shows captured behavioral data
```

#### Day 2: Backend API + Risk Engine
```
Tasks:
├── FastAPI backend with core routes
│   ├── POST /api/v1/register
│   ├── POST /api/v1/login (with behavioral assessment)
│   ├── POST /api/v1/assess-transaction
│   └── GET /api/v1/audit/trail/{user_id}
├── Database models (SQLite)
│   ├── User (with enrollment_phase flag)
│   ├── BehavioralBaseline (Behavioral DNA)
│   ├── DeviceFingerprint
│   ├── LoginLog (with all scores)
│   └── BehavioralEvent
├── Risk Engine (rule-based Phase 1)
│   ├── behavioral_scorer.py → z-score from baseline
│   ├── device_scorer.py → Jaccard fingerprint match
│   ├── context_scorer.py → time anomaly check
│   ├── composite_scorer.py → weighted formula
│   └── response_protocol.py → score → action mapping
├── Auth: JWT + bcrypt
└── Test: curl/Postman → verify scores returned
```

#### Day 3: Integration + Demo Polish
```
Tasks:
├── Connect frontend ↔ backend
│   ├── Login flow end-to-end with real scoring
│   ├── Registration → enrollment phase
│   └── Dashboard with risk score display
├── Build "Security Dashboard" panel
│   ├── Real-time risk score gauge
│   ├── Sub-score breakdown (behavioral, device, context)
│   ├── XAI reasons panel
│   └── Audit trail table
├── Enrollment flow: 5-session baseline building
├── Seed demo data: pre-register a test user with baseline
└── Test: Full demo flow rehearsal
```

### Phase 2: Advanced Features (Days 4-5) — SHOULD COMPLETE

```
Tasks:
├── Isolation Forest integration (trained on pre-seeded data)
├── Failed login behavioral profiling
├── Continuous auth (SSE-based score push during session)
├── Transaction gate (step-up on Send Money)
├── MPIN/UPI PIN entry with keystroke capture
├── Comparison demo mode (real user vs impersonator visualization)
└── Audit logger with SHAP-style reasons
```

### Phase 3: Polish + Documentation (Day 6) — NICE TO HAVE

```
Tasks:
├── README.md (GitHub-ready with badges, screenshots)
├── Architecture documentation
├── Docker one-command setup
├── Edge case handling
└── Demo rehearsal and timing
```

---

## Technology Stack (Simplified for PoC)

| Layer | Technology | Justification |
|-------|-----------|---------------|
| **Frontend** | HTML5 + CSS3 + Vanilla JS | Zero dependencies, fast to build, easy to demo |
| **Backend** | Python 3.11 + FastAPI | Async, fast, auto-docs at /docs, type validation |
| **ML (Phase 1)** | NumPy + SciPy | Z-score behavioral scoring — works with 1 session |
| **ML (Phase 2)** | scikit-learn (Isolation Forest) | Add when enough data exists |
| **Database** | SQLite | Zero setup, single file, sufficient for demo |
| **Auth** | JWT (PyJWT) + bcrypt (passlib) | Industry standard |
| **XAI** | Custom reason mapper | Maps deviations → human-readable strings |

### Why NOT These Alternatives

| Alternative | Why Not for PoC |
|-------------|-----------------|
| React/Next.js | Adds build step, node_modules, complexity — vanilla JS looks just as good with proper CSS |
| PostgreSQL | Needs Docker/install — SQLite is zero-config |
| PyTorch (LSTM) | Heavy dependency, needs training data, no demo value |
| SHAP library | Slow computation, overkill for demo — custom reasons are faster |
| Redis | Unnecessary for single-user demo — Python dict works |
| MongoDB | Extra dependency — JSON file storage works |

---

## Frontend vs Framework Decision

### Pros of Vanilla HTML/CSS/JS (Recommended ✅)
1. **Zero build step** — open HTML in browser, done
2. **No node_modules** — cleaner repo, faster setup
3. **Easier to debug** — no virtual DOM, no React DevTools needed
4. **FastAPI serves static files** — one server for everything
5. **Judges see clean code** — no framework abstraction layer
6. **Premium UI achievable** — CSS custom properties + glassmorphism + animations

### Cons of Vanilla (Manageable)
1. No component reusability → **Mitigate:** Use JS template literals for repeated UI
2. No state management → **Mitigate:** Simple JS object store
3. No routing → **Mitigate:** Multi-page app (each HTML is a route)

### When to Switch to React/Vite
- If you need real-time dashboard with 10+ updating components
- If the demo needs SPA feel with animated page transitions
- If team has React experience and can move faster with it

**Verdict for hackathon: Vanilla JS wins.** Time saved on setup = time spent on demo polish.

---

## File Structure (Minimal PoC — What We Actually Build)

```
kavach/
├── README.md                           # GitHub-ready documentation
├── .gitignore                          # Python + IDE ignores
├── .env.example                        # Environment template
├── requirements.txt                    # Python dependencies
│
├── frontend/                           # Web UI
│   ├── index.html                      # Landing → redirect to login
│   ├── login.html                      # Login with behavioral capture
│   ├── register.html                   # Registration form
│   ├── dashboard.html                  # Banking dashboard (3 actions)
│   ├── send-money.html                 # UPI Send Money flow
│   ├── history.html                    # Transaction history
│   ├── security.html                   # Security/Risk dashboard
│   ├── css/
│   │   └── style.css                   # Premium dark theme
│   └── js/
│       ├── kavach-sdk.js               # Behavioral Collector SDK
│       ├── login.js                    # Login flow
│       ├── register.js                 # Registration flow
│       ├── dashboard.js                # Dashboard + continuous auth
│       └── utils.js                    # API helpers, JWT storage
│
├── backend/                            # FastAPI Backend
│   ├── main.py                         # FastAPI app + all routes
│   ├── config.py                       # Configuration
│   ├── database.py                     # SQLite connection
│   ├── models.py                       # SQLAlchemy models
│   ├── schemas.py                      # Pydantic schemas
│   ├── auth.py                         # JWT + bcrypt
│   ├── risk_engine/
│   │   ├── __init__.py
│   │   ├── composite_scorer.py         # Weighted risk formula
│   │   ├── behavioral_scorer.py        # Keystroke anomaly detection
│   │   ├── device_scorer.py            # Fingerprint matching
│   │   ├── context_scorer.py           # Time + location checks
│   │   ├── failed_login_scorer.py      # Failed attempt analysis
│   │   └── response_protocol.py        # Score → action
│   ├── enrollment/
│   │   ├── __init__.py
│   │   ├── enrollment_manager.py       # 5-session gate
│   │   └── baseline_builder.py         # Behavioral DNA
│   ├── continuous_auth/
│   │   ├── __init__.py
│   │   └── rolling_scorer.py           # Session re-scoring
│   └── audit/
│       ├── __init__.py
│       └── audit_logger.py             # JSON audit log
│
├── ml_engine/                          # ML Models
│   ├── __init__.py
│   ├── feature_extractor.py            # All feature extraction
│   ├── isolation_forest.py             # IF model (Phase 2)
│   ├── behavioral_dna.py              # Statistical profiling
│   └── reason_mapper.py               # XAI reason strings
│
├── docs/                               # Documentation
│   ├── ARCHITECTURE.md                 # System architecture
│   ├── API_REFERENCE.md                # API docs
│   └── INDIAN_SCENARIO.md             # India-specific context
│
├── data/                               # Runtime data (gitignored)
│   ├── kavach.db                       # SQLite database
│   ├── events/                         # Behavioral event JSONs
│   ├── audit/                          # Audit logs
│   └── models/                         # Trained model pickles
│
└── tests/                              # Core tests only
    ├── test_risk_engine.py
    └── test_feature_extractor.py
```

**Total: ~35 files** (vs 65+ in original plan). Half the files, same demo impact.
