from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import itertools

from db.database import get_db
import crud
import schemas
from pinecone_service import pinecone_service
from embedding_service import embedding_service
from llm_service import llm_service

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Oracles of Norway AI Readings API"}

@app.get("/decks/", response_model=List[schemas.Deck])
def read_decks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    decks = crud.get_decks(db, skip=skip, limit=limit)
    return decks

@app.get("/decks/{deck_id}", response_model=schemas.Deck)
def read_deck(deck_id: int, db: Session = Depends(get_db)):
    db_deck = crud.get_deck(db, deck_id=deck_id)
    if db_deck is None:
        raise HTTPException(status_code=404, detail="Deck not found")
    return db_deck

@app.post("/readings/")
def create_reading(request: schemas.ReadingRequest, db: Session = Depends(get_db)):
    if not request.card_names:
        raise HTTPException(status_code=400, detail="No card names provided.")

    # Sanitize input card names
    sanitized_card_names = [name.strip() for name in request.card_names]

    context = ""
    # A dummy vector is still needed for the dense part of the query API call
    dummy_dense_vector = [0.0] * 384 # Dimension of all-MiniLM-L6-v2

    # Step 1: Prioritize looking for a pre-written combination for two cards
    if len(sanitized_card_names) == 2:
        for perm in itertools.permutations(sanitized_card_names):
            combo_name = f"{perm[0]} and {perm[1]}"
            combo_filter = {"deck_name": request.deck_name, "card_name": combo_name}
            
            # Note: We omit sparse_vector for metadata-only searches
            search_results = pinecone_service.query(
                dense_vector=dummy_dense_vector,
                top_k=1,
                filter=combo_filter
            )
            if search_results['matches']:
                match = search_results['matches'][0]
                context += f"Combined Interpretation for {combo_name}:\n{match['metadata']['text']}\n---\n"
                break
    
    # Step 2: Fetch individual card interpretations
    for card_name in sanitized_card_names:
        card_filter = {"deck_name": request.deck_name, "card_name": card_name}
        search_results = pinecone_service.query(
            dense_vector=dummy_dense_vector,
            top_k=1,
            filter=card_filter
        )
        if search_results['matches']:
            match = search_results['matches'][0]
            context += f"Card Name: {match['metadata']['card_name']}\nInterpretation: {match['metadata']['text']}\n---\n"

    if not context:
        raise HTTPException(status_code=404, detail="Could not find context for the given cards.")

    # Step 3: Generate the reading with the LLM
    reading = llm_service.generate_reading(card_names=sanitized_card_names, context=context)

    return {"reading": reading}
