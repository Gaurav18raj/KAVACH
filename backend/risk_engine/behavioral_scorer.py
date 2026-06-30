import math
import os
import joblib
import numpy as np

# ==========================================
# KAVACH BACKEND: Behavioral Scorer
# ==========================================
# Pointwise Explanation:
# 1. This is Phase 1 of the ML implementation (Rule-based Z-Score computation).
# 2. It compares the current login's typing features (hold time, IKI) against the user's stored Behavioral DNA.
# 3. Z-Score formula: |Current_Value - Baseline_Mean| / Baseline_StdDev.
# 4. If the Z-score is very high (e.g. > 3), it means the typing is statistically anomalous (likely an attacker).
# 5. We use a Sigmoid function to normalize the infinite Z-score into a clean 0 to 1 risk score.

def compute_z_score(current_val, mean, std):
    """Calculates how many standard deviations away the current value is from the mean."""
    # Prevent division by zero if std is somehow 0 (e.g. very consistent user)
    if std == 0:
        std = 1.0 
    return abs(current_val - mean) / std

def sigmoid_normalization(z_avg):
    """
    Normalizes the Z-score to a [0, 1] range.
    A Z-score of 2 (2 std devs away) is mapped to roughly 0.5 risk.
    Higher Z-scores asymptotically approach 1.0 (Critical Risk).
    """
    # Centered so that z=2 maps to 0.5 (medium risk)
    return 1 / (1 + math.exp(-(z_avg - 2.0)))

def score_behavior(current_features, baseline_dna):
    """
    Compares the current typing payload against the stored DNA.
    Returns:
    - score (float): 0.0 (Safe) to 1.0 (Critical)
    - reasons (list): Human-readable XAI strings explaining anomalies.
    """
    reasons = []
    z_scores = []
    
    # 1. Check Hold Time (How long keys are pressed)
    z_hold = compute_z_score(current_features.hold_mean, baseline_dna.hold_mean, baseline_dna.hold_std)
    z_scores.append(z_hold)
    if z_hold > 2.5:
        reasons.append(f"Typing hold time is highly unusual (Z-Score: {z_hold:.1f})")

    # 2. Check Inter-Key Interval (The rhythm between keys)
    z_iki = compute_z_score(current_features.iki_mean, baseline_dna.iki_mean, baseline_dna.iki_std)
    z_scores.append(z_iki)
    if z_iki > 2.5:
        reasons.append(f"Typing rhythm (IKI) deviates significantly from baseline (Z-Score: {z_iki:.1f})")

    # 3. Sensor Fusion: Mouse Entropy (Network Latency / AnyDesk Check)
    mouse_ent = getattr(current_features, 'mouse_entropy', 0.0)
    if mouse_ent > 300.0:
        z_scores.append(3.0) # Highly anomalous
        reasons.append(f"CRITICAL: High Mouse Entropy ({mouse_ent:.1f}). Possible Remote Desktop (AnyDesk) latency detected.")

    # 4. Sensor Fusion: Gyroscope Haptics (Bot / Remote Access Check)
    gyro = getattr(current_features, 'gyro_angle', 0.0)
    gyro_available = getattr(current_features, 'gyro_available', False)
    
    # If gyro is completely perfectly 0 (and they didn't just fail to grant permission), it's suspicious for a mobile device.
    if gyro_available and abs(gyro) < 0.005: 
        z_scores.append(2.5)
        reasons.append("WARNING: Device is perfectly flat during typing. Possible automated bot or remote access.")

    # 5. --- TRUE ML UPGRADE: Isolation Forest Inference ---
    # Check if a trained Isolation Forest model exists for this user
    model_path = f"models/user_{baseline_dna.user_id}_iforest.pkl"
    ml_score = None
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            current_vector = np.array([[current_features.hold_mean, current_features.iki_mean]])
            # decision_function returns > 0 for inliers, < 0 for outliers
            # Lower score = more anomalous. Let's invert it for our 0-1 risk scale.
            anomaly_score = model.decision_function(current_vector)[0]
            if anomaly_score < 0:
                reasons.append(f"ML ISOLATION FOREST: Anomaly Detected (Score: {anomaly_score:.2f})")
                z_scores.append(3.0) # Treat as high risk
            else:
                reasons.append(f"ML ISOLATION FOREST: Behavior matches authentic signature (Score: {anomaly_score:.2f})")
                z_scores.append(0.0) # Treat as completely safe
            ml_score = True
        except Exception as e:
            print(f"Failed to load/run Isolation Forest: {e}")

    # 6. Aggregate
    if ml_score:
        # If ML model ran successfully, we rely heavily on its decision for the behavioral part.
        avg_z = sum(z_scores) / len(z_scores)
    else:
        avg_z = sum(z_scores) / len(z_scores) if z_scores else 0
        
    final_score = sigmoid_normalization(avg_z)
    
    # Cap very low scores to 0 to prevent noise
    if final_score < 0.1:
        final_score = 0.0

    return final_score, reasons
