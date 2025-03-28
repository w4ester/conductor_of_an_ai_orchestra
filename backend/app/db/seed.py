# app/db/seed.py
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from uuid import uuid4

def seed_db():
    db = SessionLocal()
    try:
        # Add default users if they don't exist
        if db.query(User).filter(User.email == "user@example.com").first() is None:
            regular_user = User(
                id=str(uuid4()),
                email="user@example.com",
                username="workshopuser",
                full_name="Workshop User",
                hashed_password=get_password_hash("password"),
                disabled=False,
                is_admin=False
            )
            db.add(regular_user)
        
        if db.query(User).filter(User.email == "admin@example.com").first() is None:
            admin_user = User(
                id=str(uuid4()),
                email="admin@example.com",
                username="admin",
                full_name="Workshop Admin",
                hashed_password=get_password_hash("admin"),
                disabled=False,
                is_admin=True
            )
            db.add(admin_user)
        
        db.commit()
        print("Database seeded successfully")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
