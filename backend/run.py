# run.py
import uvicorn
from app.db.seed import seed_db
from app.db.database import Base, engine

if __name__ == "__main__":
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Seed the database
    seed_db()
    
    # Run the application
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
