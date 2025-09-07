#!/usr/bin/env python3
"""
Database initialization script for production deployment.
This script creates the database tables and loads initial data.
"""

import os
import sys
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import engine
from db.models import Base
from crud import create_deck, create_card
from sqlalchemy.orm import sessionmaker

def init_database():
    """Initialize the database with tables and basic data"""
    print("Creating database tables...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")
    
    # Create a session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create basic decks if they don't exist
        from db.models import Deck
        
        decks_data = [
            {"name": "SENSITIVE SOUL"},
            {"name": "LIGHT FROM NORTH STOCK"},
            {"name": "ROUNDED ORACLES ARR"},
            {"name": "EVERYDAY ORACLES ARR"},
            {"name": "HEALING CARDS"},
            {"name": "SPIRITUAL AWARENESS CARDS"},
            {"name": "two_card_combinations"},
            {"name": "three_card_combinations"},
            {"name": "five_card_combinations"}
        ]
        
        for deck_data in decks_data:
            existing_deck = db.query(Deck).filter_by(name=deck_data["name"]).first()
            if not existing_deck:
                deck = Deck(name=deck_data["name"])
                db.add(deck)
                print(f"✓ Created deck: {deck_data['name']}")
            else:
                print(f"✓ Deck already exists: {deck_data['name']}")
        
        db.commit()
        print("✓ Database initialization completed successfully")
        
    except Exception as e:
        print(f"✗ Error during database initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
