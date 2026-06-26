import os

# ==========================================
# KAVACH BACKEND: Configuration Settings
# ==========================================
# Detailed Breakdown:
# 1. SECRET_KEY: Used for JWT encoding. In a real app, this MUST be in an .env file.
# 2. ALGORITHM: HS256 is standard for JWT.
# 3. ACCESS_TOKEN_EXPIRE_MINUTES: Short expiry (30 mins) ensures that if a session is hijacked, it dies quickly.
# 4. ENROLLMENT_SESSIONS: The number of sessions required to build the user's Behavioral DNA before activating ML.

SECRET_KEY = os.environ.get("SECRET_KEY", "hackathon_super_secret_kavach_key_999")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# The number of logins needed before ML kicks in. (Cold Start Problem solution)
ENROLLMENT_SESSIONS = 5

# Risk Formula Weights (Production Mode)
# - Behavioral (typing rhythm) is the strongest indicator (40%)
# - Device (fingerprint) is strong but spoofable (25%)
# - Context (time/location) provides environmental hints (20%)
# - Failed Logins provides threat context (15%)
WEIGHT_BEHAVIORAL = 0.40
WEIGHT_DEVICE = 0.25
WEIGHT_CONTEXT = 0.20
WEIGHT_FAILED_LOGIN = 0.15

# Risk Formula Weights (Enrollment Mode - No ML)
# During the first 5 sessions, we don't have typing baseline, so we rely on device and context.
ENROLL_WEIGHT_DEVICE = 0.70
ENROLL_WEIGHT_CONTEXT = 0.30

# SQLite URL for easy demo deployment without Docker/Postgres
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/kavach.db"
