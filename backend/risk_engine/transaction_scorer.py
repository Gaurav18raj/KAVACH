import datetime

def score_transaction(user_profile, amount: float, recipient_upi: str, db, user_id: int):
    """
    Computes the Kavach Ledger Intelligence (KLI) Transaction Risk Score.
    Follows the "Deepak vs Albert" ledger model.
    """
    risk_score = 0.0
    reasons = []

    # If the user has no spending profile yet, assume it's a new account
    if not user_profile or user_profile.avg_txn_amount == 0.0:
        return 0.2, ["WARNING: No transaction history available for baseline. Moderate risk applied."]

    # ==========================================
    # SIGNAL 1: Amount Deviation Score (45% weight)
    # ==========================================
    # Example: Deepak avg Rs 40. Attempts 2500 -> 62x deviation
    # Albert avg Rs 1000. Attempts 2500 -> 2.5x deviation
    deviation_ratio = amount / user_profile.avg_txn_amount
    amount_deviation_score = min(1.0, deviation_ratio / 10.0) 
    
    if deviation_ratio > 10.0:
        reasons.append(f"CRITICAL: Transaction amount is {deviation_ratio:.1f}x above normal for this user.")
    elif deviation_ratio > 5.0:
        reasons.append(f"WARNING: Transaction amount is unusually high ({deviation_ratio:.1f}x average).")
        
    risk_score += (0.45 * amount_deviation_score)

    # ==========================================
    # SIGNAL 2: Velocity Score (10% weight)
    # ==========================================
    from ..models import TransactionHistory
    two_hours_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=2)
    recent_txns = db.query(TransactionHistory).filter(
        TransactionHistory.user_id == user_id,
        TransactionHistory.timestamp >= two_hours_ago
    ).count()

    velocity_ratio = recent_txns / max(1.0, user_profile.velocity_norm)
    velocity_score = min(1.0, velocity_ratio / 3.0) # 3x normal velocity is max risk

    if velocity_ratio > 3.0:
        reasons.append(f"HIGH RISK: {recent_txns} rapid transactions detected in last 2 hours. Velocity attack pattern.")
        
    risk_score += (0.10 * velocity_score)

    # ==========================================
    # SIGNAL 3: Recipient Trust (30% weight)
    # ==========================================
    known_recipient = db.query(TransactionHistory).filter(
        TransactionHistory.user_id == user_id,
        TransactionHistory.recipient_upi == recipient_upi
    ).first()

    if not known_recipient:
        recipient_score = 0.7
        reasons.append("WARNING: Unknown recipient outside trusted network.")
        if amount > user_profile.avg_txn_amount * 3:
            recipient_score = 1.0 # Unknown + large amount
            reasons.append("CRITICAL: Large transfer to unknown recipient.")
    else:
        recipient_score = 0.0
        reasons.append(f"INFO: Recipient {recipient_upi} is a trusted contact.")

    risk_score += (0.30 * recipient_score)

    # ==========================================
    # SIGNAL 4: Time of Day (10% weight)
    # ==========================================
    current_hour = datetime.datetime.now().hour
    # Check if current_hour is inside the active window
    if user_profile.active_hours_start <= user_profile.active_hours_end:
        is_active = user_profile.active_hours_start <= current_hour <= user_profile.active_hours_end
    else:
        # Crosses midnight
        is_active = current_hour >= user_profile.active_hours_start or current_hour <= user_profile.active_hours_end

    time_score = 0.0 if is_active else 1.0
    if not is_active:
        reasons.append(f"ANOMALY: Transaction time outside user's normal behavioral window.")
    
    risk_score += (0.10 * time_score)

    # ==========================================
    # SIGNAL 5: Budget Exhaustion (5% weight)
    # ==========================================
    first_of_month = datetime.datetime.now(datetime.timezone.utc).replace(day=1, hour=0, minute=0, second=0)
    month_txns = db.query(TransactionHistory).filter(
        TransactionHistory.user_id == user_id,
        TransactionHistory.timestamp >= first_of_month
    ).all()
    
    month_total = sum([t.amount for t in month_txns])
    projected_total = month_total + amount
    
    if user_profile.monthly_total_cap > 0:
        budget_ratio = projected_total / user_profile.monthly_total_cap
        budget_score = min(1.0, budget_ratio - 1.0) if budget_ratio > 1.0 else 0.0
        
        if budget_ratio > 1.5:
            reasons.append(f"HIGH RISK: This transaction would exceed normal monthly cap by {int((budget_ratio - 1.0) * 100)}%.")
            
        risk_score += (0.05 * budget_score)
    
    return min(1.0, risk_score), reasons
