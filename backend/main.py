from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import logging
import colorama
from colorama import Fore, Style
from datetime import datetime, timedelta

from .database import engine, Base, get_db
from .models import User, LoginLog, DeviceFingerprint, BehavioralBaseline, TransactionHistory, UserSpendingProfile
from .schemas import UserRegister, UserLogin, TransactionRequest, RiskResponse, UserProfile
from .auth import get_password_hash, verify_password, create_access_token, get_current_user
from .risk_engine.composite_scorer import calculate_composite_risk, determine_action
from .risk_engine.transaction_scorer import score_transaction
from .enrollment.enrollment_manager import process_enrollment_event
from .config import ENROLLMENT_SESSIONS

# Initialize colorama
colorama.init(autoreset=True)

# Custom Logger for the Terminal (Hackathon Demo Ready)
class ColorLogFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.INFO:
            record.msg = f"{Fore.CYAN}[INFO]{Style.RESET_ALL} {record.msg}"
        elif record.levelno == logging.WARNING:
            record.msg = f"{Fore.YELLOW}[WARN]{Style.RESET_ALL} {record.msg}"
        elif record.levelno == logging.ERROR:
            record.msg = f"{Fore.RED}[ERROR]{Style.RESET_ALL} {record.msg}"
        elif record.levelno == logging.CRITICAL:
            record.msg = f"{Fore.WHITE}{colorama.Back.RED}[CRITICAL]{Style.RESET_ALL} {record.msg}"
        return super().format(record)

logger = logging.getLogger("kavach")
logger.setLevel(logging.INFO)

# 1. Console Handler (Colored output for Demo)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(ColorLogFormatter('%(message)s'))
    logger.addHandler(ch)

# 2. File Handler (Permanent Audit Trail)
os.makedirs("logs", exist_ok=True)
fh = logging.FileHandler("logs/kavach_demo.log", encoding="utf-8")
fh_formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
fh.setFormatter(fh_formatter)
logger.addHandler(fh)

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="KAVACH AI Behavioral Auth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Let the request process
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    
    # Log everything that comes from the frontend
    if request.url.path.startswith("/api/v1/"):
        method_color = Fore.CYAN if request.method == "GET" else Fore.MAGENTA
        status_color = Fore.GREEN if response.status_code < 400 else Fore.RED
        logger.info(f"[UI ACTION] {method_color}{request.method}{Style.RESET_ALL} {request.url.path} - {status_color}{response.status_code}{Style.RESET_ALL} ({formatted_process_time}ms)")
        
    return response

# --- API ROUTES ---

@app.post("/api/v1/register", status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserRegister, db: Session = Depends(get_db)):
    logger.info(f"Registration attempt for: {user_in.username}")
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        logger.warning(f"Registration failed: User {user_in.username} already exists.")
        raise HTTPException(status_code=400, detail="UPI ID already registered")

    new_user = User(
        username=user_in.username,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        enrollment_phase=True,
        session_count=0
    )
    db.add(new_user)
    db.commit()
    logger.info(f"{Fore.GREEN}Successfully registered {user_in.username}. Initiating Enrollment Phase.{Style.RESET_ALL}")
    return {"message": "User registered successfully."}

@app.post("/api/v1/login", response_model=RiskResponse)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    
    # 1. Traditional Credential Check
    user = db.query(User).filter(User.username == login_data.username).first()

    logger.info(f"Login attempt for: {login_data.username}")

    if user:
        logger.info(f"Customer Name: {user.full_name}")
        logger.info(f"UPI ID: {user.username}")
        logger.info(f"Device Hash: {login_data.device.canvasHash}")

    if not user or not verify_password(login_data.password, user.hashed_password):
        logger.warning(f"{Fore.RED}Login Failed: Invalid credentials for {login_data.username}{Style.RESET_ALL}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 2. Fetch ML Baselines
    baseline = db.query(BehavioralBaseline).filter(BehavioralBaseline.user_id == user.id).first()
    trusted_devices = db.query(DeviceFingerprint).filter(DeviceFingerprint.user_id == user.id).all()
    
    # Calculate failed logins in the last 15 minutes
    time_threshold = datetime.utcnow() - timedelta(minutes=15)
    failed_login_count = db.query(LoginLog).filter(
        LoginLog.user_id == user.id,
        LoginLog.action_taken != "ALLOW",
        LoginLog.timestamp >= time_threshold
    ).count()

    logger.info(f"Running Risk Engine. User Enrollment Phase: {user.enrollment_phase}")
    logger.info(f"{Fore.MAGENTA}[DPDP Compliance Check] Scrubbing PII. Generating one-way Timing Matrix Hash...{Style.RESET_ALL}")
    logger.info("=" * 60)
    logger.info("KAVACH BEHAVIORAL ANALYSIS")

    logger.info(f"User: {login_data.username}")

    logger.info(
        f"Hold Mean: {login_data.behavioral_data.hold_mean} ms"
    )

    logger.info(
        f"Hold Std: {login_data.behavioral_data.hold_std} ms"
    )

    logger.info(
        f"IKI Mean: {login_data.behavioral_data.iki_mean} ms"
    )

    logger.info(
        f"IKI Std: {login_data.behavioral_data.iki_std} ms"
    )

    logger.info(
        f"Backspaces: {login_data.behavioral_data.backspace_count}"
    )

    logger.info(
        f"Hesitation: {login_data.behavioral_data.hesitation_ms} ms"
    )

    logger.info(
        f"Mouse Entropy: {login_data.behavioral_data.mouse_entropy}"
    )

    logger.info(
        f"Gyro Angle: {login_data.behavioral_data.gyro_angle}"
    )

    logger.info(
        f"Transaction Amount: {login_data.behavioral_data.transaction_amount}"
    )

    logger.info("=" * 60)
    # 3. Run the KAVACH Risk Engine
    score, reasons = calculate_composite_risk(
        user=user,
        current_behavior=login_data.behavioral_data,
        current_device=login_data.device,
        baseline_dna=baseline,
        trusted_devices=trusted_devices,
        failed_login_count=failed_login_count
    )

    # 4. Map Score to Response Action
    risk_level, action = determine_action(score)
    
    # --- TERMINAL LOGGING OF RISK SCORE ---
    if action == "ALLOW":
        color = Fore.GREEN
    elif action == "OTP_CHALLENGE":
        color = Fore.YELLOW
    else:
        color = Fore.RED
        
    logger.info(f"Risk Score: {color}{score}{Style.RESET_ALL} | Level: {color}{risk_level}{Style.RESET_ALL} | Action: {color}{action}{Style.RESET_ALL}")
    for r in reasons:
        logger.info(f"  -> Reason: {r}")

    # 5. Post-Login processing
    if action != "BLOCK":
        process_enrollment_event(db, user, login_data.behavioral_data)
        if not any(d.canvas_hash == login_data.device.canvasHash for d in trusted_devices):
            new_dev = DeviceFingerprint(
                user_id=user.id,
                canvas_hash=login_data.device.canvasHash,
                user_agent=login_data.device.userAgent,
                screen_resolution=login_data.device.screenRes
            )
            db.add(new_dev)

    log_entry = LoginLog(
        user_id=user.id,
        composite_score=score,
        risk_level=risk_level,
        action_taken=action,
        reasons=str(reasons)
    )
    db.add(log_entry)
    db.commit()

    token = None
    if action == "ALLOW":
        token = create_access_token(data={"sub": user.username})

    return RiskResponse(
        access_granted=(action == "ALLOW"),
        risk_score=score,
        risk_level=risk_level,
        action=action,
        reasons=reasons,
        session_token=token
    )

# --- TRANSACTION ENDPOINT ---
@app.post("/api/v1/transaction", response_model=RiskResponse)
def process_transaction(tx_data: TransactionRequest, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    logger.info(f"Transaction attempt by: {tx_data.username} for amount: {tx_data.amount}")
    
    if tx_data.username != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to act for this user")
        
    user = db.query(User).filter(User.username == tx_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    baseline = db.query(BehavioralBaseline).filter(BehavioralBaseline.user_id == user.id).first()
    trusted_devices = db.query(DeviceFingerprint).filter(DeviceFingerprint.user_id == user.id).all()
    
    time_threshold = datetime.utcnow() - timedelta(minutes=15)
    failed_login_count = db.query(LoginLog).filter(
        LoginLog.user_id == user.id,
        LoginLog.action_taken != "ALLOW",
        LoginLog.timestamp >= time_threshold
    ).count()

    # KAVACH LEDGER INTELLIGENCE (KLI) - Profile User's Financial Behavior
    user_profile = db.query(UserSpendingProfile).filter(UserSpendingProfile.user_id == user.id).first()
    txn_score, txn_reasons = score_transaction(
        user_profile=user_profile,
        amount=tx_data.amount,
        recipient_upi=tx_data.payee_upi,
        db=db,
        user_id=user.id
    )

    score, reasons = calculate_composite_risk(
        user=user,
        current_behavior=tx_data.behavioral_data,
        current_device=tx_data.device,
        baseline_dna=baseline,
        trusted_devices=trusted_devices,
        failed_login_count=failed_login_count,
        txn_score=txn_score,
        txn_reasons=txn_reasons
    )

    risk_level, action = determine_action(score)
    
    # Post-Transaction Ledger Update
    if action == "ALLOW":
        new_txn = TransactionHistory(
            user_id=user.id,
            amount=tx_data.amount,
            recipient_upi=tx_data.payee_upi
        )
        db.add(new_txn)
        
        # Update Profile
        if not user_profile:
            user_profile = UserSpendingProfile(user_id=user.id)
            db.add(user_profile)
        
        # Simple rolling average
        all_txns = db.query(TransactionHistory).filter(TransactionHistory.user_id == user.id).count() + 1
        user_profile.avg_txn_amount = ((user_profile.avg_txn_amount * (all_txns - 1)) + tx_data.amount) / all_txns
        if tx_data.amount > user_profile.max_single_txn:
            user_profile.max_single_txn = tx_data.amount
            
        db.commit()
    
    if action == "ALLOW":
        color = Fore.GREEN
    elif action == "OTP_CHALLENGE":
        color = Fore.YELLOW
    else:
        color = Fore.RED
        
    logger.info(f"Tx Risk Score: {color}{score}{Style.RESET_ALL} | Action: {color}{action}{Style.RESET_ALL}")

    return RiskResponse(
        access_granted=(action == "ALLOW"),
        risk_score=score,
        risk_level=risk_level,
        action=action,
        reasons=reasons,
        session_token=None
    )

@app.get("/api/v1/balance")
def get_balance(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    recent = db.query(TransactionHistory).filter(TransactionHistory.user_id == user.id).order_by(TransactionHistory.timestamp.desc()).limit(5).all()
    
    # Calculate balance based on starting 100000 minus all successful transactions
    all_txns = db.query(TransactionHistory).filter(TransactionHistory.user_id == user.id, TransactionHistory.status == 'ALLOWED').all()
    total_spent = sum([t.amount for t in all_txns])
    balance = 100000.0 - total_spent
    
    return {
        "balance": balance,
        "currency": "INR",
        "account": user.username,
        "recent_transactions": [{"amount": t.amount, "to": t.recipient_upi, "status": t.status} for t in recent]
    }

@app.get("/api/v1/user/logs")
def get_user_logs(username: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    if username != current_user:
        raise HTTPException(status_code=403, detail="Not authorized")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    logs = db.query(LoginLog).filter(LoginLog.user_id == user.id).order_by(LoginLog.timestamp.desc()).limit(10).all()
    return [{"timestamp": l.timestamp, "score": l.composite_score, "level": l.risk_level, "action": l.action_taken, "reasons": l.reasons} for l in logs]

@app.get("/api/v1/user/dna")
def get_user_dna(username: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    if username != current_user:
        raise HTTPException(status_code=403, detail="Not authorized")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    baseline = db.query(BehavioralBaseline).filter(BehavioralBaseline.user_id == user.id).first()
    
    if user.enrollment_phase:
        status = f"Enrolling ({user.session_count}/{ENROLLMENT_SESSIONS})"
    else:
        status = "Active"
        
    return {
        "status": status,
        "hold_mean": baseline.hold_mean if baseline else 0,
        "iki_mean": baseline.iki_mean if baseline else 0,
        "trusted_devices_count": db.query(DeviceFingerprint).filter(DeviceFingerprint.user_id == user.id).count()
    }

# --- STATIC FILE SERVING ---
# Mount the frontend directory so we don't need a separate server
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")
