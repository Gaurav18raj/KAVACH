from ..config import (
    WEIGHT_BEHAVIORAL, WEIGHT_DEVICE, WEIGHT_CONTEXT, WEIGHT_FAILED_LOGIN,
    ENROLL_WEIGHT_DEVICE, ENROLL_WEIGHT_CONTEXT
)
from .behavioral_scorer import score_behavior
from .device_scorer import score_device
from .context_scorer import score_context

# ==========================================
# KAVACH BACKEND: Composite Scorer
# ==========================================
# Pointwise Explanation:
# 1. This orchestrates all the individual scorers.
# 2. It applies the Phase Gate:
#    - If user is in ENROLLMENT (First 5 sessions): ML is muted. We only use Device and Context.
#    - If user is in PRODUCTION: We use the full 4-pillar risk formula.
# 3. Aggregates all human-readable reasons for the Audit Trail / Security Dashboard.

def calculate_composite_risk(user, current_behavior, current_device, baseline_dna, trusted_devices):
    """
    [ADVANCED RISK SCORING ALGORITHM]
    Role: Orchestrates the calculation of the final risk score by fusing multiple intelligence streams.
    
    Usage / Function:
    This function acts as the central brain of the KAVACH system. It implements a Zero-Trust 
    Continuous Authentication model specifically designed to counteract Indian banking fraud 
    (e.g., Jamtara screen-sharing scams, reverse-proxy phishing). 

    It operates in two distinct phases:
    1. Phase 1 (Enrollment): If user.enrollment_phase == True, the ML model is MUTED to prevent 
       Cold Start false positives. Only Device (70%) and Context (30%) are evaluated.
    2. Phase 2 (Production): Full 4-pillar ML formula is applied.
       Formula: Score = 0.40(Behavioral) + 0.25(Device) + 0.20(Context) + 0.15(FailedLogins)
       
    Why this is critical for the Indian Scenario:
    Even if a scammer has the correct password and intercepted the OTP, their typing rhythm 
    (Behavioral score) and Device fingerprint will catastrophically fail this composite check, 
    resulting in a Block action.
    """
    all_reasons = []
    composite_score = 0.0
    
    # 1. Device Scoring (Always runs)
    d_score, d_reasons = score_device(current_device, trusted_devices)
    all_reasons.extend(d_reasons)
    
    # 2. Context Scoring (Always runs)
    c_score, c_reasons = score_context(current_device)
    all_reasons.extend(c_reasons)

    # 3. Phase Gate Application
    if user.enrollment_phase:
        # NO BEHAVIORAL SCORING YET.
        # Fallback to rule-based device/context scoring.
        composite_score = (ENROLL_WEIGHT_DEVICE * d_score) + (ENROLL_WEIGHT_CONTEXT * c_score)
        all_reasons.append("INFO: Account in Enrollment Phase. Behavioral ML is muted.")
    else:
        # FULL ML PRODUCTION MODE
        b_score, b_reasons = score_behavior(current_behavior, baseline_dna)
        all_reasons.extend(b_reasons)
        
        # Formula: 0.40(B) + 0.25(D) + 0.20(C) + 0.15(F)
        # Note: Failed login scorer is mocked as 0 for this immediate login flow MVP
        f_score = 0.0 
        
        composite_score = (
            (WEIGHT_BEHAVIORAL * b_score) +
            (WEIGHT_DEVICE * d_score) +
            (WEIGHT_CONTEXT * c_score) +
            (WEIGHT_FAILED_LOGIN * f_score)
        )
        
        if not b_reasons and not d_reasons and not c_reasons:
            all_reasons.append("All signals normal. Rhythm matches Behavioral DNA.")

    return round(composite_score, 2), all_reasons

def determine_action(score):
    """
    Maps the composite score to a risk level and a concrete action.
    """
    if score < 0.25:
        return "LOW", "ALLOW"
    elif score < 0.50:
        return "MEDIUM", "OTP_CHALLENGE"
    elif score < 0.72:
        return "HIGH", "BIOMETRIC_STEP_UP"
    else:
        return "CRITICAL", "BLOCK"
