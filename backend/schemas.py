from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# ==========================================
# KAVACH BACKEND: Pydantic Schemas
# ==========================================
# Pointwise Explanation:
# 1. Pydantic is used for strict type checking on incoming API requests.
# 2. BehavioralData Schema enforces the exact payload expected from the kavach-sdk.js frontend.
# 3. DeviceData Schema ensures device intelligence is passed correctly.
# 4. RiskResponse Schema is the standardized output format the frontend expects to display alerts.

# --- Input Schemas ---

class UserRegister(BaseModel):
    full_name: str
    username: str
    password: str

class BehavioralData(BaseModel):
    hold_mean: float
    hold_std: float
    iki_mean: float
    iki_std: float
    mouse_entropy: Optional[float] = 0.0      # Advanced Sensor Fusion
    gyro_angle: Optional[float] = 0.0         # Advanced Sensor Fusion
    transaction_amount: Optional[float] = 0.0 # Hierarchical UPI Scaling
    backspace_count: int
    hesitation_ms: float

class DeviceData(BaseModel):
    userAgent: str
    screenRes: str
    timezoneOffset: int
    language: str
    canvasHash: str

class UserLogin(BaseModel):
    username: str
    password: str
    behavioral_data: BehavioralData
    device: DeviceData

# --- Output Schemas ---

class RiskResponse(BaseModel):
    access_granted: bool
    risk_score: float
    risk_level: str
    action: str
    reasons: List[str]
    session_token: Optional[str] = None
    
class UserProfile(BaseModel):
    username: str
    full_name: str
    enrollment_phase: bool
    session_count: int
