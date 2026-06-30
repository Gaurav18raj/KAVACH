from sqlalchemy.orm import Session
from ..models import User, BehavioralBaseline
from ..config import ENROLLMENT_SESSIONS
import json
import statistics
import os
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

# ==========================================
# KAVACH BACKEND: Enrollment Manager
# ==========================================
# Pointwise Explanation:
# 1. Manages the "Cold Start" phase.
# 2. When a user first registers, they have no baseline typing pattern.
# 3. We record their typing silently for the first N sessions (default 5).
# 4. Once they hit the threshold, we build the DNA and switch `enrollment_phase` to False.
# 5. This triggers the Risk Engine to start using the Isolation Forest / Z-score ML logic on future logins.

def process_enrollment_event(db: Session, user: User, behavioral_data):
    """
    Called after a successful login. 
    If the user is in enrollment phase, we increment their session count and
    update their baseline averages.
    """
    if not user.enrollment_phase:
        return # They are already in production mode.

    # 1. Fetch or create their baseline
    baseline = db.query(BehavioralBaseline).filter(BehavioralBaseline.user_id == user.id).first()
    if not baseline:
        baseline = BehavioralBaseline(user_id=user.id)
        db.add(baseline)
        db.commit()
        db.refresh(baseline)

    # 2. Store Raw Samples
    try:
        hold_samples = json.loads(baseline.hold_samples) if baseline.hold_samples else []
    except:
        hold_samples = []
    
    try:
        iki_samples = json.loads(baseline.iki_samples) if baseline.iki_samples else []
    except:
        iki_samples = []

    hold_samples.append(behavioral_data.hold_mean)
    iki_samples.append(behavioral_data.iki_mean)

    baseline.hold_samples = json.dumps(hold_samples)
    baseline.iki_samples = json.dumps(iki_samples)

    # Update Rolling Mean
    current_count = user.session_count
    baseline.hold_mean = ((baseline.hold_mean * current_count) + behavioral_data.hold_mean) / (current_count + 1)
    baseline.iki_mean = ((baseline.iki_mean * current_count) + behavioral_data.iki_mean) / (current_count + 1)
    
    # 3. Increment Session Count
    user.session_count += 1
    
    # 4. Phase Gate Check (Graduation)
    if user.session_count >= ENROLLMENT_SESSIONS:
        user.enrollment_phase = False
        
        # Calculate actual population standard deviation based on collected samples
        if len(hold_samples) > 1:
            baseline.hold_std = statistics.stdev(hold_samples)
        else:
            baseline.hold_std = 15.0 # fallback

        if len(iki_samples) > 1:
            baseline.iki_std = statistics.stdev(iki_samples)
        else:
            baseline.iki_std = 25.0 # fallback

        # To avoid hyper-sensitivity if the user typed perfectly identically:
        if baseline.hold_std < 5.0:
            baseline.hold_std = 5.0
        if baseline.iki_std < 5.0:
            baseline.iki_std = 5.0

        # --- TRUE ML UPGRADE: Train Isolation Forest ---
        # We train an Isolation Forest on the behavioral vectors (hold, IKI)
        try:
            X_train = np.array(list(zip(hold_samples, iki_samples)))
            # We assume enrollment samples are normal (contamination='auto' or small)
            model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
            model.fit(X_train)
            
            os.makedirs("models", exist_ok=True)
            model_path = f"models/user_{user.id}_iforest.pkl"
            joblib.dump(model, model_path)
            print(f"[ML PIPELINE] Trained and saved IsolationForest for User {user.id}")
        except Exception as e:
            print(f"[ML PIPELINE ERROR] Failed to train IsolationForest: {e}")
            
    db.commit()
