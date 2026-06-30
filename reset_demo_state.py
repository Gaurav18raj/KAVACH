import os
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base, User, BehavioralBaseline
from backend.auth import get_password_hash

DB_PATH = "kavach.db"

def reset_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("[RESET] Deleted old kavach.db")
        
    if os.path.exists("models"):
        shutil.rmtree("models")
        os.makedirs("models")
        print("[RESET] Cleared ML models directory")

    engine = create_engine("sqlite:///./kavach.db")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    # Seed User 1: Deepak (Normal User)
    user1 = User(username="deepak@upi", full_name="Deepak", hashed_password=get_password_hash("password123"), enrollment_phase=True, session_count=0)
    db.add(user1)

    # Seed User 2: Alpha (Demo Setup)
    user2 = User(username="alpha@upi", full_name="Alpha", hashed_password=get_password_hash("alpha123"), enrollment_phase=True, session_count=0)
    db.add(user2)

    db.commit()
    print("[RESET] Seeded users: deepak@upi, alpha@upi")
    print("[SUCCESS] Demo state perfectly reset and ready for presentation!")

if __name__ == "__main__":
    print("==========================================")
    print(" KAVACH | Demo Reset Tool ")
    print("==========================================")
    reset_db()
