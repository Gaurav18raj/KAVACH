from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import SQLALCHEMY_DATABASE_URL

# ==========================================
# KAVACH BACKEND: Database Connection Setup
# ==========================================
# Detailed Breakdown:
# 1. We use SQLite for the hackathon MVP because it requires zero installation and is highly portable.
# 2. check_same_thread=False is needed for FastAPI since it handles requests concurrently.
# 3. SessionLocal is a factory for database sessions. Each request gets its own session.
# 4. Base is the declarative base class for our SQLAlchemy models.

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to inject DB session into FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
