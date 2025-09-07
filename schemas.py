from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class CardBase(BaseModel):
    name: str
    interpretation: str

class Card(CardBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class DeckBase(BaseModel):
    name: str

class Deck(DeckBase):
    id: int
    cards: List[Card] = []
    model_config = ConfigDict(from_attributes=True)

class ReadingRequest(BaseModel):
    deck_name: str
    card_names: List[str]
    alpha: float = 0.5
    theme: str = "default"  # Theme for the reading
    user_query: Optional[str] = None  # Optional user question/query
