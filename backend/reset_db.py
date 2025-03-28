#!/usr/bin/env python
# reset_db.py
"""
Script to reset the database and re-seed it.
"""
import os
import sys

# Set environment variable to reset the database
os.environ["RESET_DB"] = "true"

# Import database components after setting environment variable
from app.db.database import Base, engine
from app.db.seed import seed_db

def reset_database():
    """Reset database by dropping all tables and recreating them."""
    print("Resetting database...")
    
    # Drop all tables (will be recreated by Base.metadata.create_all)
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Seed the database
    seed_db()
    
    print("Database has been reset and re-seeded.")

if __name__ == "__main__":
    # Confirm reset unless --force flag is provided
    if "--force" not in sys.argv:
        response = input("This will delete all data in the database. Continue? (y/n): ")
        if response.lower() != "y":
            print("Database reset cancelled.")
            sys.exit(0)
    
    reset_database()
