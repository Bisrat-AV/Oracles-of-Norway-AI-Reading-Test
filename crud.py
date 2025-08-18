from sqlalchemy.orm import Session
from db import models
import schemas

def get_deck(db: Session, deck_id: int):
    return db.query(models.Deck).filter(models.Deck.id == deck_id).first()

def get_decks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Deck).offset(skip).limit(limit).all()

def get_card(db: Session, card_id: int):
    return db.query(models.Card).filter(models.Card.id == card_id).first()

def get_cards_by_deck(db: Session, deck_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Card).filter(models.Card.deck_id == deck_id).offset(skip).limit(limit).all()
