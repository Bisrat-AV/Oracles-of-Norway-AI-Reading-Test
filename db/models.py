from sqlalchemy import Column, Integer, String, Text, UniqueConstraint, ForeignKey, Identity
from sqlalchemy.orm import declarative_base, relationship

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
