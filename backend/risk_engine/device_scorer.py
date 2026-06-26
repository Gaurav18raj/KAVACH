# ==========================================
# KAVACH BACKEND: Device Scorer
# ==========================================
# Pointwise Explanation:
# 1. Scammers often use new devices or Emulators to log in.
# 2. This module compares the incoming browser fingerprint against the user's historically trusted devices.
# 3. We use a simplified Jaccard-style matching for the MVP.
# 4. If the Canvas Hash and Screen Res don't match, risk goes up.

def score_device(current_device, trusted_devices):
    """
    Scores the device based on match percentage.
    Returns score (0.0 = Trusted, 1.0 = Completely Unknown) and reasons.
    """
    reasons = []
    
    if not trusted_devices:
        # Implicitly trust the very first device used to log in.
        return 0.0, ["First device login - implicitly trusted and added to baseline."]

    best_match_score = 1.0 # 1.0 means worst risk initially
    
    for trusted in trusted_devices:
        mismatches = 0
        total_checks = 3
        
        # Check 1: Canvas Hash (Browser graphics rendering quirk)
        if current_device.canvasHash != trusted.canvas_hash:
            mismatches += 1
            
        # Check 2: Screen Resolution
        if current_device.screenRes != trusted.screen_resolution:
            mismatches += 1
            
        # Check 3: User Agent 
        if current_device.userAgent != trusted.user_agent:
            mismatches += 1
            
        risk_for_this_device = mismatches / total_checks
        
        if risk_for_this_device < best_match_score:
            best_match_score = risk_for_this_device

    # Generate reasons if there is some risk
    if best_match_score > 0.3:
        reasons.append("Unrecognized device fingerprint detected")
    if best_match_score == 1.0:
        reasons.append("Device matches NO known historical devices")

    return best_match_score, reasons
