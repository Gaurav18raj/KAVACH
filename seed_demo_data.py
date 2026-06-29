import os
import random
from datetime import datetime, timedelta, timezone

from backend.database import SessionLocal, engine, Base
from backend.models import User, TransactionHistory, UserSpendingProfile, BehavioralBaseline, DeviceFingerprint
from backend.auth import get_password_hash

# Initialize DB
Base.metadata.create_all(bind=engine)

def seed_demo_data():
    db = SessionLocal()
    
    friends = [
        {
            "username": "deepak@upi",
            "full_name": "Deepak",
            "avg_amount": 42.0,
            "monthly_cap": 1500.0,
            "velocity": 0.1,
            "active_start": 21,
            "active_end": 23
        },
        {
            "username": "albert@upi",
            "full_name": "Albert",
            "avg_amount": 980.0,
            "monthly_cap": 35000.0,
            "velocity": 0.8,
            "active_start": 20,
            "active_end": 2
        },
        {
            "username": "himanshu@upi",
            "full_name": "Himanshu",
            "avg_amount": 250.0,
            "monthly_cap": 8000.0,
            "velocity": 0.3,
            "active_start": 9,
            "active_end": 22
        },
        {
            "username": "gaurav@upi",
            "full_name": "Gaurav",
            "avg_amount": 1500.0,
            "monthly_cap": 12000.0,
            "velocity": 0.05,
            "active_start": 10,
            "active_end": 20
        }
    ]

    print("[*] Clearing old demo profiles...")
    db.query(TransactionHistory).delete()
    db.query(UserSpendingProfile).delete()
    
    # We will just delete specific test users and re-insert
    for friend in friends:
        existing = db.query(User).filter(User.username == friend["username"]).first()
        if existing:
            db.delete(existing)
    db.commit()

    print("[*] Seeding 4 friend profiles...")

    for friend in friends:
        user = User(
            username=friend["username"],
            full_name=friend["full_name"],
            hashed_password=get_password_hash("password123"),
            enrollment_phase=False,
            session_count=5
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create baseline
        baseline = BehavioralBaseline(
            user_id=user.id,
            hold_mean=90.0,
            hold_std=10.0,
            iki_mean=150.0,
            iki_std=20.0
        )
        db.add(baseline)
        
        # Add trusted device
        device = DeviceFingerprint(
            user_id=user.id,
            canvas_hash=f"mock_hash_{friend['full_name'].lower()}",
            user_agent="Mocked User Agent",
            screen_resolution="1080x2340"
        )
        db.add(device)
        
        # Create spending profile
        profile = UserSpendingProfile(
            user_id=user.id,
            avg_txn_amount=friend["avg_amount"],
            max_single_txn=friend["avg_amount"] * 2,
            monthly_total_cap=friend["monthly_cap"],
            velocity_norm=friend["velocity"] * 24, # roughly daily
            active_hours_start=friend["active_start"],
            active_hours_end=friend["active_end"]
        )
        db.add(profile)
        
        # Seed 30 days of transactions
        # Generate N transactions based on daily velocity
        days = 30
        daily_txns = max(1, int(friend["velocity"] * 24))
        
        print(f"    -> Seeding {daily_txns * days} transactions for {friend['full_name']}...")
        now = datetime.now(timezone.utc)
        
        for d in range(days):
            for t in range(daily_txns):
                amount = random.uniform(friend["avg_amount"] * 0.5, friend["avg_amount"] * 1.5)
                # Generate a random time within their active hours
                start = friend["active_start"]
                end = friend["active_end"]
                
                if start > end: # crosses midnight
                    if random.random() > 0.5:
                        h = random.randint(start, 23)
                    else:
                        h = random.randint(0, end)
                else:
                    h = random.randint(start, end)
                    
                txn_time = now - timedelta(days=d)
                txn_time = txn_time.replace(hour=h, minute=random.randint(0, 59))
                
                recipient = random.choice([f["username"] for f in friends if f["username"] != friend["username"]])
                
                txn = TransactionHistory(
                    user_id=user.id,
                    amount=round(amount, 2),
                    recipient_upi=recipient,
                    timestamp=txn_time
                )
                db.add(txn)
                
        db.commit()
        
    print("\n[+] Seeding Complete! The 5 Friends demo environment is ready.")
    db.close()

if __name__ == "__main__":
    seed_demo_data()
