from sqlalchemy.orm import Session
from ..models import User, BehavioralBaseline
from ..config import ENROLLMENT_SESSIONS

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

    # 2. Incremental Mean Calculation for MVP
    # In a real app, you would store all raw events in a database and compute the true 
    # population mean and std deviation. For this fast hackathon MVP, we use a simple
    # rolling average approximation.
    current_count = user.session_count

    # New Mean = (OldMean * OldCount + NewValue) / (OldCount + 1)
    baseline.hold_mean = ((baseline.hold_mean * current_count) + behavioral_data.hold_mean) / (current_count + 1)
    baseline.iki_mean = ((baseline.iki_mean * current_count) + behavioral_data.iki_mean) / (current_count + 1)
    
    # We fake the standard deviation updating for the MVP to avoid storing large arrays.
    # We assign a default variance that the user will be judged against.
    baseline.hold_std = 15.0 # assume +/- 15ms consistency is normal
    baseline.iki_std = 25.0  # assume +/- 25ms consistency is normal

    # 3. Increment Session Count
    user.session_count += 1
    
    # 4. Phase Gate Check
    if user.session_count >= ENROLLMENT_SESSIONS:
        # User has graduated! Welcome to Production Continuous Auth.
        user.enrollment_phase = False

    db.commit()
