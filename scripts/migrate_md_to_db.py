import os
import hashlib
from db.database import SessionLocal
from db.models import Base, MarkdownFile
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_engine():
    return create_engine(DATABASE_URL)

def create_tables(engine):
    # Drop and recreate tables to update schema
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

def load_md_files_to_db():
    """Load existing .md files into the database"""
    engine = get_engine()
    create_tables(engine)
    
    db = SessionLocal()
    
    # Define file mappings with their types
    md_files = {
        'data/oracle_cards_by_deck.md': 'oracle_cards',
        'data/two_card_readings.md': 'two_card_readings',
        'data/three_card_readings.md': 'three_card_readings',
        'data/five_card_readings.md': 'five_card_readings'
    }
    
    for filename, file_type in md_files.items():
        if os.path.exists(filename):
            print(f"Loading {filename} into database as type: {file_type}")
            
            # Read file content
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate content hash
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            print(f"  - Content hash: {content_hash[:16]}...")
            
            # Check if file already exists in database (by hash or filename)
            existing_file = db.query(MarkdownFile).filter(
                (MarkdownFile.content_hash == content_hash) | 
                (MarkdownFile.filename == filename)
            ).first()
            
            if existing_file:
                print(f"  - Updating existing record for {filename}")
                existing_file.content = content
                existing_file.content_hash = content_hash
                existing_file.file_type = file_type
            else:
                print(f"  - Creating new record for {filename}")
                md_file = MarkdownFile(
                    content_hash=content_hash,
                    filename=filename,
                    content=content,
                    file_type=file_type
                )
                db.add(md_file)
        else:
            print(f"Warning: {filename} not found")
    
    db.commit()
    print("Migration completed successfully!")
    
    # Verify the data was saved
    files = db.query(MarkdownFile).all()
    print(f"Verification: {len(files)} files saved to database")
    for f in files:
        print(f"  - {f.filename} ({f.file_type}) - Hash: {f.content_hash[:16]}... (content length: {len(f.content)})")
    
    db.close()

if __name__ == "__main__":
    load_md_files_to_db()
