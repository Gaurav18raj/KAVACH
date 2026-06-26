from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from .database import Base

# ==========================================
# KAVACH BACKEND: Database Models
# ==========================================
# Pointwise Explanation:
# 1. User Model: 
#    - Stores core user identity.
#    - 'enrollment_phase' flags whether the user is building their baseline (first 5 sessions) or in production.
#    - No sensitive KYC data (Aadhaar, PAN) is stored here, aligning with RBI Data Minimization.
# 2. BehavioralBaseline Model:
#    - Stores the statistical "Behavioral DNA" (mean, std, skew).
#    - PRIVACY BY DESIGN: By storing averages and standard deviations instead of raw key presses, 
#      it is mathematically impossible to reverse-engineer the user's password.
# 3. LoginLog Model:
#    - Essential for the Audit Trail required by CERT-In and RBI guidelines.
#    - Stores the composite risk score and the action taken (e.g., ALLOW, STEP_UP).
# 4. DeviceFingerprint Model:
#    - Stores the hashes of trusted devices. If a scammer uses AnyDesk or a different phone, this fails.

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True) # UPI ID format e.g. ramesh@upi
    full_name = Column(String)
    hashed_password = Column(String)
    
    # KAVACH Specific Fields
    enrollment_phase = Column(Boolean, default=True) # True for first 5 sessions
    session_count = Column(Integer, default=0)       # Tracks progress towards baseline
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class BehavioralBaseline(Base):
    __tablename__ = "behavioral_baselines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Statistical moments representing the "Behavioral DNA"
    hold_mean = Column(Float, default=0.0)
    hold_std = Column(Float, default=0.0)
    iki_mean = Column(Float, default=0.0)
    iki_std = Column(Float, default=0.0)
    typing_speed_cps = Column(Float, default=0.0)
    mouse_entropy_avg = Column(Float, default=0.0)
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class LoginLog(Base):
    __tablename__ = "login_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # KAVACH Scoring Data
    composite_score = Column(Float)
    risk_level = Column(String)     # LOW, MEDIUM, HIGH, CRITICAL
    action_taken = Column(String)   # ALLOW, OTP, BLOCK
    reasons = Column(String)        # JSON string of XAI reasons
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class DeviceFingerprint(Base):
    __tablename__ = "device_fingerprints"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Hardware/Software identifiers
    canvas_hash = Column(String)
    user_agent = Column(String)
    screen_resolution = Column(String)
    
    trust_score = Column(Float, default=1.0)
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
