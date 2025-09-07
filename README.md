# Oracles of Norway AI Readings

An intelligent oracle card reading system that provides personalized readings using AI, with support for multiple themes and card combinations.

## Project Structure

```
OraclesOfNorwayAIReadings/
├── main.py                 # FastAPI application entry point
├── crud.py                 # Database CRUD operations
├── schemas.py              # Pydantic models for API
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── db/                    # Database layer
│   ├── __init__.py
│   ├── database.py        # Database connection and session
│   └── models.py          # SQLAlchemy models
│
├── services/              # Core business logic services
│   ├── __init__.py
│   ├── embedding_service.py    # Text embedding and vectorization
│   ├── llm_service.py          # OpenAI LLM integration
│   ├── pinecone_service.py     # Vector database operations
│   └── prompt_service.py       # Prompt management and themes
│
├── prompts/               # YAML prompt files
│   ├── base_prompt.yaml       # Base system prompts and examples
│   ├── theme_default.yaml     # Default reading theme
│   ├── theme_general.yaml     # General reading theme
│   ├── theme_healing.yaml     # Healing & support theme
│   ├── theme_manifestation.yaml # Manifestation theme
│   ├── theme_growth.yaml      # Growth & development theme
│   └── theme_inspiration.yaml # Inspiration theme
│
├── data/                  # Data files and assets
│   ├── __init__.py
│   ├── oracle_cards_by_deck.md    # Individual card interpretations
│   ├── two_card_readings.md       # Pre-written 2-card combinations
│   ├── three_card_readings.md     # Pre-written 3-card combinations
│   ├── five_card_readings.md      # Pre-written 5-card combinations
│   ├── tfidf_vectorizer.joblib    # Trained TF-IDF vectorizer
│   └── API_DOCUMENTATION.md       # API documentation
│
├── scripts/               # Utility scripts
│   ├── __init__.py
│   ├── migrate_md_to_db.py       # Load markdown files to database
│   └── process_data.py           # Process and embed data
│
├── tests/                 # Test files
│   ├── __init__.py
│   ├── test_process_data.py      # Data processing tests
│   └── test_prompt_system.py     # Prompt system tests
│
└── venv/                  # Python virtual environment
```

## Features

- **Multiple Oracle Decks**: 6 different oracle card decks with 318+ cards
- **Smart Card Combinations**: Pre-written interpretations for 2, 3, and 5-card combinations
- **5 Reading Themes**: Specialized perspectives (General, Healing, Manifestation, Growth, Inspiration)
- **User Query Integration**: Personalized readings based on user questions
- **Hybrid Search**: Combines semantic and keyword search for accurate card retrieval
- **Robust Card Search**: Case-insensitive, fuzzy matching with automatic fallback to alternative decks
- **AI Synthesis**: Fallback AI generation for custom combinations

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   Create a `.env` file with:
   ```
   DATABASE_URL=your_database_url
   PINECONE_API_KEY=your_pinecone_key
   OPENAI_API_KEY=your_openai_key
   ```

3. **Load Data**:
   ```bash
   python scripts/migrate_md_to_db.py
   python scripts/process_data.py
   ```

4. **Start Server**:
   ```bash
   uvicorn main:app --port 8000 --reload
   ```

5. **Access API**:
   - API Documentation: `http://127.0.0.1:8000/docs`
   - Available Themes: `http://127.0.0.1:8000/themes/`
   - Generate Reading: `POST http://127.0.0.1:8000/readings/`

## API Usage

### Generate a Reading

```bash
curl -X POST "http://127.0.0.1:8000/readings/" \
  -H "Content-Type: application/json" \
  -d '{
    "deck_name": "SENSITIVE SOUL",
    "card_names": ["Roots", "Blister"],
    "theme": "healing",
    "user_query": "I feel stuck in old patterns"
  }'
```

### Robust Search Features

The API now includes robust search capabilities:

- **Case Insensitive**: `"brown field"` matches `"Brown Field"`
- **Fuzzy Matching**: Handles minor typos and variations
- **Automatic Fallback**: If cards aren't found in the specified deck, searches other decks
- **Flexible Combinations**: Supports multiple combination formats (`"Card1, Card2"`, `"Card1 and Card2"`)

**Examples of robust requests that now work:**

```bash
# Case insensitive
{
  "deck_name": "five_card_combinations",
  "card_names": ["the yellow light", "THE MAILBOX", "sparkle in the eye", "brown field", "waves in the sea"],
  "theme": "manifestation"
}

# Wrong deck name (falls back to other decks)
{
  "deck_name": "WRONG_DECK",
  "card_names": ["Radiant Light", "Toxic Energy"],
  "theme": "healing"
}
```

### Available Themes

- `default/general`: Balanced, clear insights
- `healing`: Comfort and reassurance
- `manifestation`: Conscious creation focus
- `growth`: Learning and development
- `inspiration`: Creativity and openness

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Adding New Themes
1. Create a new YAML file in `prompts/theme_[name].yaml`
2. Follow the existing theme structure
3. The theme will be automatically available via the API

### Adding New Card Data
1. Add markdown files to `data/` directory
2. Update `scripts/migrate_md_to_db.py` to include new files
3. Run migration and processing scripts

## Architecture

The system uses a modular architecture with clear separation of concerns:

- **Database Layer** (`db/`): SQLAlchemy models and database operations
- **Service Layer** (`services/`): Core business logic and external integrations
- **API Layer** (`main.py`, `schemas.py`, `crud.py`): FastAPI endpoints and data validation
- **Data Layer** (`data/`): Static files and trained models
- **Scripts** (`scripts/`): Utility scripts for data management

## Dependencies

- **FastAPI**: Web framework
- **SQLAlchemy**: Database ORM
- **OpenAI**: LLM integration
- **Pinecone**: Vector database
- **SentenceTransformers**: Text embeddings
- **scikit-learn**: TF-IDF vectorization
- **PyYAML**: Prompt file parsing
