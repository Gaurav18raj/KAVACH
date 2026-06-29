from datetime import datetime

# ==========================================
# KAVACH BACKEND: Context Scorer
# ==========================================
# Pointwise Explanation:
# 1. Analyzes environmental factors: Time of login, geographic location.
# 2. In this MVP, we focus on the Timezone mismatch.
# 3. If the user's device reports a timezone in Russia, but the IP is from India, that's a massive red flag (proxy/VPN usage).

def score_context(current_device):
    """
    Scores environmental context.
    Returns score (0.0 to 1.0) and reasons.
    """
    score = 0.0
    reasons = []
    
    # Check 1: Standard Indian Timezone Offset is -330 mins (Asia/Kolkata)
    # If the user is logging in with a completely different timezone offset, flag it.
    if current_device.timezoneOffset != -330:
        # It's not inherently fraudulent to travel, but it increases risk slightly.
        score += 0.1
        reasons.append(f"INFO: Device timezone offset ({current_device.timezoneOffset}) differs from India standard. Possible NRI or VPN.")

    return min(score, 1.0), reasons
