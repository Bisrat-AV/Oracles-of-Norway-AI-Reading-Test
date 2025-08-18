import re
from db.database import SessionLocal
from db.models import Base, Deck, Card
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_engine():
    return create_engine(DATABASE_URL)

def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

def parse_oracle_cards_by_deck(filepath):
    print(f"Parsing oracle cards from: {filepath}")
    decks = {}
    with open(filepath, 'r') as f:
        content = f.read()

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

def parse_two_card_readings(filepath):
    print(f"Parsing two-card readings from: {filepath}")
    decks = {}
    current_deck = None
    with open(filepath, 'r') as f:
        content = f.read()
    
    deck_match = re.search(r'# Deck: (.*)', content)
    if deck_match:
        current_deck = deck_match.group(1).strip()
        print(f"  Found deck: {current_deck}")
        decks[current_deck] = []

    card_sections = re.split(r'---', content)
    card_count = 0
    for section in card_sections:
        card_matches = re.findall(r'## (.*?)\n(.*?)(?=\n## |\Z)', section, re.DOTALL)
        for card_name, interpretation in card_matches:
            if current_deck:
                decks[current_deck].append({
                    "name": card_name.strip(),
                    "interpretation": interpretation.strip()
                })
                card_count += 1
    print(f"    - Found {card_count} cards.")
    return decks

if __name__ == "__main__":
    engine = get_engine()
    create_tables(engine)
    
    db = SessionLocal()

    all_decks_data = {}
    all_decks_data.update(parse_oracle_cards_by_deck('oracle_cards_by_deck.md'))
    all_decks_data.update(parse_two_card_readings('two_card_readings.md'))

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
    db.close()
    print("\nData processing complete. Database has been updated.")
