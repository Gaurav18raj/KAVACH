from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import logging
import colorama
from colorama import Fore, Style

from .database import engine, Base, get_db
from .models import User, LoginLog, DeviceFingerprint, BehavioralBaseline
from .schemas import UserRegister, UserLogin, RiskResponse, UserProfile
from .auth import get_password_hash, verify_password, create_access_token
from .risk_engine.composite_scorer import calculate_composite_risk, determine_action
from .enrollment.enrollment_manager import process_enrollment_event

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    logger.info(f"Login attempt for: {login_data.username}")
    
    # 1. Traditional Credential Check
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        logger.warning(f"{Fore.RED}Login Failed: Invalid credentials for {login_data.username}{Style.RESET_ALL}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 2. Fetch ML Baselines
    baseline = db.query(BehavioralBaseline).filter(BehavioralBaseline.user_id == user.id).first()
    trusted_devices = db.query(DeviceFingerprint).filter(DeviceFingerprint.user_id == user.id).all()

    logger.info(f"Running Risk Engine. User Enrollment Phase: {user.enrollment_phase}")

    # 3. Run the KAVACH Risk Engine
    score, reasons = calculate_composite_risk(
        user=user,
        current_behavior=login_data.behavioral_data,
        current_device=login_data.device,
        baseline_dna=baseline,
        trusted_devices=trusted_devices
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
        if action == "ALLOW" and not any(d.canvas_hash == login_data.device.canvasHash for d in trusted_devices):
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

# --- STATIC FILE SERVING ---
# Mount the frontend directory so we don't need a separate server
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")
