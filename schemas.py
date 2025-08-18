from pydantic import BaseModel
from typing import List

class CardBase(BaseModel):
    name: str
    interpretation: str

class Card(CardBase):
    id: int

    class Config:
        orm_mode = True

class DeckBase(BaseModel):
    name: str

class Deck(DeckBase):
    id: int
    cards: List[Card] = []

    class Config:
        orm_mode = True
