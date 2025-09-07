from sqlalchemy import Column, Integer, String, Text, UniqueConstraint, ForeignKey, Identity, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Deck(Base):
    __tablename__ = 'decks'
    id = Column(Integer, Identity(start=1), primary_key=True)
    name = Column(String, unique=True, nullable=False)
    cards = relationship("Card", back_populates="deck")

class Card(Base):
    __tablename__ = 'cards'
    id = Column(Integer, Identity(start=1), primary_key=True)
    deck_id = Column(Integer, ForeignKey('decks.id'), nullable=False)
    name = Column(String, nullable=False)
    interpretation = Column(Text)
    deck = relationship("Deck", back_populates="cards")
    __table_args__ = (UniqueConstraint('deck_id', 'name', name='_deck_card_uc'),)

class MarkdownFile(Base):
    __tablename__ = 'markdown_files'
    id = Column(Integer, Identity(start=1), primary_key=True)
    content_hash = Column(String(64), unique=True, nullable=False, index=True)  # SHA-256 hash
    filename = Column(String, nullable=False, index=True)  # Original filename for reference
    content = Column(Text, nullable=False)
    file_type = Column(String, nullable=True, index=True)  # e.g., 'oracle_cards', 'two_card_readings'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
