import re
from db.database import SessionLocal
from db.models import Base, Deck, Card, MarkdownFile
from sqlalchemy import create_engine
import os
import sys
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.embedding_service import embedding_service
from services.pinecone_service import pinecone_service

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_engine():
    return create_engine(DATABASE_URL)

def create_tables(engine):
    # Only create tables, don't drop them to preserve existing data
    Base.metadata.create_all(engine)

def parse_oracle_cards_by_deck(file_identifier, db=None):
    print(f"Parsing oracle cards from database file: {file_identifier}")
    decks = {}
    
    if db is None:
        db = SessionLocal()
    
    # Get content from database - try multiple search methods
    md_file = None
    
    # Method 1: Search by file_type
    md_file = db.query(MarkdownFile).filter_by(file_type=file_identifier).first()
    
    # Method 2: Search by filename
    if not md_file:
        md_file = db.query(MarkdownFile).filter_by(filename=file_identifier).first()
    
    # Method 3: Search by content hash (if identifier is a hash)
    if not md_file and len(file_identifier) == 64:
        md_file = db.query(MarkdownFile).filter_by(content_hash=file_identifier).first()
    
    if not md_file:
        print(f"Error: {file_identifier} not found in database")
        if db is None:
            db.close()
        return decks
    
    content = md_file.content
    print(f"  Found file: {md_file.filename} (hash: {md_file.content_hash[:16]}...)")

    deck_sections = re.split(r'# Deck: ', content)
    for section in deck_sections:
        if not section.strip():
            continue
        
        lines = section.strip().split('\n')
        deck_name = lines[0].strip()
        print(f"  Found deck: {deck_name}")
        decks[deck_name] = []
        
        current_card = None
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('## '):
                current_card = {"name": line[3:].strip(), "interpretation": ""}
                decks[deck_name].append(current_card)
            elif current_card and line:
                current_card["interpretation"] += line + "\n"
        print(f"    - Found {len(decks[deck_name])} cards.")
    return decks

def parse_two_card_readings(file_identifier, db=None):
    print(f"Parsing two-card readings from database file: {file_identifier}")
    decks = {}
    
    if db is None:
        db = SessionLocal()
    
    # Get content from database - try multiple search methods
    md_file = None
    
    # Method 1: Search by file_type
    md_file = db.query(MarkdownFile).filter_by(file_type=file_identifier).first()
    
    # Method 2: Search by filename
    if not md_file:
        md_file = db.query(MarkdownFile).filter_by(filename=file_identifier).first()
    
    # Method 3: Search by content hash (if identifier is a hash)
    if not md_file and len(file_identifier) == 64:
        md_file = db.query(MarkdownFile).filter_by(content_hash=file_identifier).first()
    
    if not md_file:
        print(f"Error: {file_identifier} not found in database")
        if db is None:
            db.close()
        return decks
    
    content = md_file.content
    print(f"  Found file: {md_file.filename} (hash: {md_file.content_hash[:16]}...)")
    
    # For two-card readings, we'll use a generic deck name since they don't specify deck
    deck_name = "two_card_combinations"
    print(f"  Processing two-card combinations")
    decks[deck_name] = []

    card_sections = re.split(r'---', content)
    for section in card_sections:
        section_content = section.strip()
        if not section_content:
            continue
        
        # Find the header with two card names (look for both ## and ### headers)
        header_match = re.search(r'^(##|###) (.*)', section_content, re.MULTILINE)
        
        if not header_match:
            continue

        header_level, card_name = header_match.groups()
        card_name = card_name.strip()
        
        
        # The interpretation is everything after the header
        interpretation_start = section_content.find(card_name) + len(card_name)
        interpretation = section_content[interpretation_start:].strip()
        
        # Split the two card names (assuming "Card A and Card B" format)
        combined_cards = [c.strip() for c in card_name.split(" and ")]

        decks[deck_name].append({
            "name": card_name,
            "interpretation": interpretation,
            "is_combination": True,
            "combined_cards": combined_cards
        })
    
    print(f"    - Found {len(decks[deck_name])} two-card combinations.")
    return decks

def parse_three_card_readings(file_identifier, db=None):
    print(f"Parsing three-card readings from database file: {file_identifier}")
    decks = {}
    
    if db is None:
        db = SessionLocal()
    
    # Get content from database - try multiple search methods
    md_file = None
    
    # Method 1: Search by file_type
    md_file = db.query(MarkdownFile).filter_by(file_type=file_identifier).first()
    
    # Method 2: Search by filename
    if not md_file:
        md_file = db.query(MarkdownFile).filter_by(filename=file_identifier).first()
    
    # Method 3: Search by content hash (if identifier is a hash)
    if not md_file and len(file_identifier) == 64:
        md_file = db.query(MarkdownFile).filter_by(content_hash=file_identifier).first()
    
    if not md_file:
        print(f"Error: {file_identifier} not found in database")
        if db is None:
            db.close()
        return decks
    
    content = md_file.content
    print(f"  Found file: {md_file.filename} (hash: {md_file.content_hash[:16]}...)")
    
    # For three-card readings, we'll use a generic deck name since they don't specify deck
    deck_name = "three_card_combinations"
    print(f"  Processing three-card combinations")
    decks[deck_name] = []

    card_sections = re.split(r'---', content)
    for section in card_sections:
        section_content = section.strip()
        if not section_content:
            continue
        
        # Find the header with three card names
        header_match = re.search(r'^## (.*)', section_content, re.MULTILINE)
        
        if not header_match:
            continue

        card_name = header_match.group(1).strip()
        
        # The interpretation is everything after the header
        interpretation_start = section_content.find(card_name) + len(card_name)
        interpretation = section_content[interpretation_start:].strip()
        
        # Split the three card names (assuming comma separation)
        combined_cards = [c.strip() for c in card_name.split(", ")]

        decks[deck_name].append({
            "name": card_name,
            "interpretation": interpretation,
            "is_combination": True,
            "combined_cards": combined_cards
        })
    
    print(f"    - Found {len(decks[deck_name])} three-card combinations.")
    return decks

def parse_five_card_readings(file_identifier, db=None):
    print(f"Parsing five-card readings from database file: {file_identifier}")
    decks = {}
    
    if db is None:
        db = SessionLocal()
    
    # Get content from database - try multiple search methods
    md_file = None
    
    # Method 1: Search by file_type
    md_file = db.query(MarkdownFile).filter_by(file_type=file_identifier).first()
    
    # Method 2: Search by filename
    if not md_file:
        md_file = db.query(MarkdownFile).filter_by(filename=file_identifier).first()
    
    # Method 3: Search by content hash (if identifier is a hash)
    if not md_file and len(file_identifier) == 64:
        md_file = db.query(MarkdownFile).filter_by(content_hash=file_identifier).first()
    
    if not md_file:
        print(f"Error: {file_identifier} not found in database")
        if db is None:
            db.close()
        return decks
    
    content = md_file.content
    print(f"  Found file: {md_file.filename} (hash: {md_file.content_hash[:16]}...)")
    
    # For five-card readings, we'll use a generic deck name since they don't specify deck
    deck_name = "five_card_combinations"
    print(f"  Processing five-card combinations")
    decks[deck_name] = []

    card_sections = re.split(r'---', content)
    for section in card_sections:
        section_content = section.strip()
        if not section_content:
            continue
        
        # Find the header with five card names
        header_match = re.search(r'^## (.*)', section_content, re.MULTILINE)
        
        if not header_match:
            continue

        card_name = header_match.group(1).strip()
        
        # The interpretation is everything after the header
        interpretation_start = section_content.find(card_name) + len(card_name)
        interpretation = section_content[interpretation_start:].strip()
        
        # Split the five card names (assuming comma separation)
        combined_cards = [c.strip() for c in card_name.split(", ")]

        decks[deck_name].append({
            "name": card_name,
            "interpretation": interpretation,
            "is_combination": True,
            "combined_cards": combined_cards
        })
    
    print(f"    - Found {len(decks[deck_name])} five-card combinations.")
    return decks

if __name__ == "__main__":
    engine = get_engine()
    create_tables(engine)
    
    db = SessionLocal()

    # We need to process decks and cards in a way that handles combinations
    all_decks_data = {}
    deck_one_data = parse_oracle_cards_by_deck('oracle_cards', db)
    all_decks_data.update(deck_one_data)
    
    deck_two_data = parse_two_card_readings('two_card_readings', db)
    deck_three_data = parse_three_card_readings('three_card_readings', db)
    deck_five_data = parse_five_card_readings('five_card_readings', db)

    # Add all combination decks (they don't overlap with individual card decks)
    all_decks_data.update(deck_two_data)
    all_decks_data.update(deck_three_data)
    all_decks_data.update(deck_five_data)

    deck_map = {}
    print("\nProcessing and adding decks to the database...")
    for deck_name in all_decks_data:
        deck = db.query(Deck).filter_by(name=deck_name).first()
        if not deck:
            print(f"  - Adding new deck: {deck_name}")
            deck = Deck(name=deck_name)
            db.add(deck)
        else:
            print(f"  - Deck already exists: {deck_name}")
        deck_map[deck_name] = deck
    
    db.flush()
    print("\nFlushed decks to the database.")

    print("\nProcessing and adding cards to the database...")
    total_cards_added = 0
    for deck_name, cards in all_decks_data.items():
        deck = deck_map[deck_name]
        print(f"  For deck '{deck_name}':")
        for card_data in cards:
            # We don't store combinations as separate cards in the DB, only in Pinecone.
            if card_data.get("is_combination", False):
                continue
            card = db.query(Card).filter_by(deck_id=deck.id, name=card_data['name']).first()
            if not card:
                print(f"    - Adding new card: {card_data['name']}")
                card = Card(deck_id=deck.id, name=card_data['name'], interpretation=card_data['interpretation'])
                db.add(card)
                total_cards_added += 1
            else:
                print(f"    - Card already exists: {card_data['name']}")
    
    print(f"\nCommitting {len(deck_map)} decks and {total_cards_added} new cards to the database.")
    db.commit()

    # Step 2: Assemble corpus and train sparse vectorizer
    print("\nAssembling corpus for sparse vectorizer...")
    all_db_cards = db.query(Card).all()
    corpus = [card.interpretation for card in all_db_cards]
    embedding_service.fit_sparse_vectorizer(corpus)

    # Step 3: Initialize Pinecone index
    dimension = len(embedding_service.generate_embeddings("test")[0])
    pinecone_service.create_and_connect_index(dimension)

    # Step 4: Generate and upsert embeddings for ALL items (cards and combos)
    print("\nGenerating and upserting embeddings to Pinecone...")
    pinecone_id_counter = 1
    for deck_name, cards_and_combos in all_decks_data.items():
        deck = deck_map[deck_name]
        for item in cards_and_combos:
            dense_vector, sparse_vector = embedding_service.generate_embeddings(item['interpretation'])
            
            metadata = {
                "text": item['interpretation'],
                "deck_name": deck.name,
                "card_name": item['name'],
                "is_combination": item.get('is_combination', False),
                "combined_cards": item.get('combined_cards', [])
            }

            pinecone_service.upsert_card(
                id=str(pinecone_id_counter),
                dense_vector=dense_vector,
                sparse_vector=sparse_vector,
                metadata=metadata
            )
            pinecone_id_counter += 1
    
    print("\nAll cards and combinations have been embedded and upserted to Pinecone.")
    db.close()
