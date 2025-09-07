from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import itertools
import hashlib
from datetime import datetime
import os

from db.database import get_db
from db.models import MarkdownFile
import crud
import schemas
from services.pinecone_service import pinecone_service
from services.embedding_service import embedding_service
from services.llm_service import llm_service
from services.prompt_service import prompt_service
from services.card_search_service import card_search_service

# Create FastAPI app with production settings
app = FastAPI(
    title="Oracles of Norway AI Readings API",
    description="An intelligent oracle card reading system that provides personalized readings using AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Oracles of Norway AI Readings API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

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

@app.get("/themes/")
def get_available_themes():
    """Get list of available reading themes"""
    return {"themes": prompt_service.get_available_themes()}

@app.post("/readings/")
def create_reading(request: schemas.ReadingRequest, db: Session = Depends(get_db)):
    if not request.card_names:
        raise HTTPException(status_code=400, detail="No card names provided.")

    # Sanitize input card names
    sanitized_card_names = [name.strip() for name in request.card_names]

    context = ""
    # A dummy vector is still needed for the dense part of the query API call
    dummy_dense_vector = [0.0] * 384 # Dimension of all-MiniLM-L6-v2

    # Step 1: Prioritize looking for a pre-written combination (robust search)
    num_cards = len(sanitized_card_names)
    combination_found = False
    
    # Try to find a pre-written combination using robust search
    combination_match = card_search_service.find_combination_robust(sanitized_card_names, num_cards)
    
    if combination_match:
        combo_name = combination_match['metadata']['card_name']
        context += f"Combined Interpretation for {combo_name}:\n{combination_match['metadata']['text']}\n---\n"
        combination_found = True
    
    # Step 2: Fetch individual card interpretations (only if no combination found)
    if not combination_found:
        found_cards, found_all = card_search_service.find_cards_robust(sanitized_card_names, request.deck_name)
        
        if found_cards:
            for match in found_cards:
                context += f"Card Name: {match['metadata']['card_name']}\nInterpretation: {match['metadata']['text']}\n---\n"
        
        # If we couldn't find all cards, try alternative decks
        if not found_all:
            # Try searching in other decks for missing cards
            alternative_decks = ["lightFromNorthStock", "roundedOraclesArr", "everydayOraclesArr", 
                               "healingCards", "spiritualAwarenessCards"]
            
            for deck in alternative_decks:
                if deck != request.deck_name:
                    alt_found_cards, alt_found_all = card_search_service.find_cards_robust(sanitized_card_names, deck)
                    if alt_found_cards:
                        for match in alt_found_cards:
                            context += f"Card Name: {match['metadata']['card_name']} (from {deck})\nInterpretation: {match['metadata']['text']}\n---\n"
                        break

    if not context:
        raise HTTPException(status_code=404, detail="Could not find context for the given cards.")

    # Step 3: Generate the reading with the LLM
    reading = llm_service.generate_reading(
        card_names=sanitized_card_names, 
        context=context,
        theme=request.theme,
        user_query=request.user_query
    )

    return {"reading": reading}

@app.post("/documents/")
def store_document(
    file: UploadFile = File(...),
    file_type: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Store a markdown document in the database"""
    
    # Validate file type
    if not file.filename.endswith('.md'):
        raise HTTPException(status_code=400, detail="Only .md files are allowed")
    
    # Read file content
    try:
        content = file.file.read().decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be valid UTF-8 text")
    
    # Generate content hash
    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    # Check if file already exists (by hash or filename)
    existing_file = db.query(MarkdownFile).filter(
        (MarkdownFile.content_hash == content_hash) | 
        (MarkdownFile.filename == file.filename)
    ).first()
    
    if existing_file:
        # Update existing file
        existing_file.content = content
        existing_file.content_hash = content_hash
        existing_file.file_type = file_type
        existing_file.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "message": "Document updated successfully",
            "filename": existing_file.filename,
            "file_type": existing_file.file_type,
            "content_hash": existing_file.content_hash,
            "content_length": len(content),
            "updated": True
        }
    else:
        # Create new file
        md_file = MarkdownFile(
            content_hash=content_hash,
            filename=file.filename,
            content=content,
            file_type=file_type
        )
        db.add(md_file)
        db.commit()
        db.refresh(md_file)
        
        return {
            "message": "Document stored successfully",
            "filename": md_file.filename,
            "file_type": md_file.file_type,
            "content_hash": md_file.content_hash,
            "content_length": len(content),
            "updated": False
        }

@app.get("/documents/")
def list_documents(
    skip: int = 0, 
    limit: int = 100, 
    file_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List stored markdown documents"""
    
    query = db.query(MarkdownFile)
    
    if file_type:
        query = query.filter(MarkdownFile.file_type == file_type)
    
    files = query.offset(skip).limit(limit).all()
    
    return {
        "documents": [
            {
                "id": f.id,
                "filename": f.filename,
                "file_type": f.file_type,
                "content_hash": f.content_hash,
                "content_length": len(f.content),
                "created_at": f.created_at,
                "updated_at": f.updated_at
            }
            for f in files
        ],
        "total": query.count()
    }

@app.get("/documents/{document_id}")
def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get a specific document by ID"""
    
    md_file = db.query(MarkdownFile).filter(MarkdownFile.id == document_id).first()
    if not md_file:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": md_file.id,
        "filename": md_file.filename,
        "file_type": md_file.file_type,
        "content_hash": md_file.content_hash,
        "content": md_file.content,
        "content_length": len(md_file.content),
        "created_at": md_file.created_at,
        "updated_at": md_file.updated_at
    }

@app.delete("/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document by ID"""
    
    md_file = db.query(MarkdownFile).filter(MarkdownFile.id == document_id).first()
    if not md_file:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(md_file)
    db.commit()
    
    return {"message": f"Document '{md_file.filename}' deleted successfully"}
