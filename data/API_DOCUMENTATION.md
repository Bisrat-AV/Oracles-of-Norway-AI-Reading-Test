# Oracles of Norway AI Readings API Documentation

This document provides an overview of the API endpoints for the Oracles of Norway AI Readings service.

## Overview

The Oracles of Norway AI Readings API provides intelligent oracle card readings with:
- **Multiple Reading Themes**: 5 specialized themes (General, Healing & Support, Manifestation, Growth & Development, Inspiration)
- **Smart Card Combinations**: Pre-written interpretations for 2, 3, and 5-card combinations
- **User Query Integration**: Personalized readings based on user questions
- **Hybrid Search**: Combines semantic and keyword search for accurate card retrieval
- **Multiple Oracle Decks**: 6 different oracle card decks with 318+ cards

## Base URL

The API is served from the root of the application. When running locally, the base URL is:
`http://127.0.0.1:8000`

---

## Authentication

There is currently no authentication required to access this API.

---

## Available Decks

The system includes the following oracle card decks:

1. **lightFromNorthStock** - 80 cards
2. **roundedOraclesArr** - 44 cards  
3. **everydayOraclesArr** - 71 cards
4. **healingCards** - 44 cards
5. **spiritualAwarenessCards** - 61 cards
6. **SENSITIVE SOUL** - 18 cards

## Reading Themes

The API supports 5 specialized reading themes:

- **default/general**: Balanced, clear, and accessible insights
- **healing**: Comfort and reassurance with gentle, compassionate guidance
- **manifestation**: Conscious creation and intention-setting focus
- **growth**: Learning, self-reflection, and personal evolution
- **inspiration**: Sparking curiosity, creativity, and openness

## Card Combinations

The system intelligently handles different card combinations:

### Pre-written Combinations
- **2-Card Combinations**: 9 pre-written interpretations (e.g., "Roots and Blister", "Radiant Light and Toxic Energy")
- **3-Card Combinations**: 3 pre-written interpretations (e.g., "Forest Mist, Midnight Sun, Pathfinder")
- **5-Card Combinations**: 3 pre-written interpretations (e.g., "The Yellow Light, The Mailbox, Sparkle in the Eye, Brown Field, Waves in the Sea")

### AI Synthesis
When no pre-written combination exists, the system:
- Fetches individual card interpretations
- Uses AI to synthesize a cohesive reading
- Includes examples for 2, 3, and 5-card combinations
- Applies theme-specific guidance

---

## Endpoints

### 1. Root

A simple welcome message to verify that the API is running.

- **Endpoint:** `GET /`
- **Method:** `GET`
- **Description:** Returns a welcome message.
- **Success Response:**
  - **Code:** 200 OK
  - **Content:** `{"message": "Welcome to the Oracles of Norway AI Readings API"}`

---

### 2. Get All Decks

Retrieves a list of all available oracle decks stored in the database.

- **Endpoint:** `GET /decks/`
- **Method:** `GET`
- **Description:** Fetches a paginated list of all oracle decks.
- **Query Parameters:**
  - `skip` (optional, integer, default: 0): The number of decks to skip from the beginning.
  - `limit` (optional, integer, default: 100): The maximum number of decks to return.
- **Success Response:**
  - **Code:** 200 OK
  - **Content:** An array of Deck objects.
- **Example Response:**
  ```json
  [
    {
      "id": 1,
      "name": "SENSITIVE SOUL",
      "cards": [
        {
          "id": 1,
          "name": "Radiant Light",
          "interpretation": "This card represents gifts and recognition..."
        }
      ]
    },
    {
      "id": 2,
      "name": "lightFromNorthStock",
      "cards": []
    }
  ]
  ```

---

### 3. Get Deck by ID

Retrieves a single oracle deck by its unique ID.

- **Endpoint:** `GET /decks/{deck_id}`
- **Method:** `GET`
- **Description:** Fetches a single deck by its primary key ID.
- **Path Parameters:**
  - `deck_id` (required, integer): The ID of the deck to retrieve.
- **Success Response:**
  - **Code:** 200 OK
  - **Content:** A single Deck object.
- **Error Response:**
  - **Code:** 404 Not Found
  - **Content:** `{"detail": "Deck not found"}`

---

### 4. Get Available Themes

Retrieves a list of all available reading themes.

- **Endpoint:** `GET /themes/`
- **Method:** `GET`
- **Description:** Fetches all available reading themes with their descriptions.
- **Success Response:**
  - **Code:** 200 OK
  - **Content:** An object containing available themes.
- **Example Response:**
  ```json
  {
    "themes": {
      "default": "Balanced, clear, and accessible insights based directly on the cards' messages",
      "general": "Balanced, clear, and accessible insights based directly on the cards' messages",
      "healing": "Comfort and reassurance when interpreting the cards, with emphasis on gentleness and acceptance",
      "manifestation": "Show how the cards' messages can be translated into conscious creation and intention-setting",
      "growth": "Emphasize learning, self-reflection, and personal evolution in light of the cards",
      "inspiration": "Spark curiosity, creativity, and openness through the cards' messages"
    }
  }
  ```

---

### 5. Generate Oracle Reading

The core endpoint for generating an AI-powered oracle reading. It uses a hybrid search (semantic and keyword) to find the most relevant card interpretations and then synthesizes a reading using an LLM.

- **Endpoint:** `POST /readings/`
- **Method:** `POST`
- **Description:** Creates a synthesized oracle reading based on a list of selected cards from a specified deck.
- **Request Body:**
  ```json
  {
    "deck_name": "SENSITIVE SOUL",
    "card_names": [
      "Radiant Light",
      "Toxic Energy"
    ],
    "alpha": 0.5,
    "theme": "healing",
    "user_query": "Should I make a major life change?"
  }
  ```
  - `deck_name` (required, string): The name of the deck from which the cards are drawn.
  - `card_names` (required, array of strings): A list of the names of the cards that were drawn.
  - `alpha` (optional, float, default: 0.5): A value between 0.0 and 1.0 to balance the hybrid search. `0.0` is pure keyword search, `1.0` is pure semantic search.
  - `theme` (optional, string, default: "default"): The reading theme/perspective to use. Available themes: "default", "general", "healing", "manifestation", "growth", "inspiration".
  - `user_query` (optional, string): An optional question or query from the user to be incorporated into the reading.
- **Success Response:**
  - **Code:** 200 OK
  - **Content:**
    ```json
    {
      "reading": "The cards Radiant Light and Toxic Energy together create a powerful dichotomy... The presence of Radiant Light suggests that you possess an inner strength and a capacity for immense good..."
    }
    ```
- **Error Responses:**
  - **Code:** 400 Bad Request
    - **Content:** `{"detail": "No card names provided."}`
  - **Code:** 404 Not Found
    - **Content:** `{"detail": "Could not find context for the given cards."}`

### Reading Examples

#### Example 1: 2-Card Reading with Pre-written Combination
```json
{
  "deck_name": "SENSITIVE SOUL",
  "card_names": ["Roots", "Blister"],
  "theme": "healing",
  "user_query": "I feel stuck in old patterns"
}
```
**Response**: Uses pre-written "Roots and Blister" combination with healing theme guidance.

#### Example 2: 3-Card Reading with AI Synthesis
```json
{
  "deck_name": "SENSITIVE SOUL",
  "card_names": ["Forest Mist", "Midnight Sun", "Pathfinder"],
  "theme": "growth",
  "user_query": "How can I find clarity in my confusion?"
}
```
**Response**: AI synthesizes individual card meanings with growth theme and user query.

#### Example 3: 5-Card Reading with Pre-written Combination
```json
{
  "deck_name": "SENSITIVE SOUL",
  "card_names": ["The Yellow Light", "The Mailbox", "Sparkle in the Eye", "Brown Field", "Waves in the Sea"],
  "theme": "manifestation",
  "user_query": "How can I manifest positive change?"
}
```
**Response**: Uses pre-written 5-card combination with manifestation theme guidance.

#### Example 4: Single Card Reading
```json
{
  "deck_name": "healingCards",
  "card_names": ["Self-love"],
  "theme": "healing",
  "user_query": "I need guidance on self-care"
}
```
**Response**: Individual card interpretation with healing theme and user query integration.

---

## Document Storage Endpoints

The API provides comprehensive document storage capabilities for managing markdown files containing oracle card data. All documents are stored with content-addressable hashing for integrity and deduplication.

### 5. Upload Document

Uploads a markdown document to the database for processing and storage.

- **Endpoint:** `POST /documents/`
- **Method:** `POST`
- **Description:** Stores a markdown file in the database with automatic content hashing and deduplication.
- **Content-Type:** `multipart/form-data`
- **Form Parameters:**
  - `file` (required, file): The markdown file to upload. Must have `.md` extension.
  - `file_type` (optional, string): A semantic identifier for the document type (e.g., "oracle_cards", "two_card_readings").
- **Success Response:**
  - **Code:** 200 OK
  - **Content:**
    ```json
    {
      "message": "Document stored successfully",
      "filename": "my_deck.md",
      "file_type": "oracle_cards",
      "content_hash": "f26837c72c2586d180ac94a60821030a7e062f93c9cff61bee9c88dfe6af87a0",
      "content_length": 391714,
      "updated": false
    }
    ```
- **Error Responses:**
  - **Code:** 400 Bad Request
    - **Content:** `{"detail": "Only .md files are allowed"}`
    - **Content:** `{"detail": "File must be valid UTF-8 text"}`

---

### 6. List Documents

Retrieves a paginated list of all stored markdown documents.

- **Endpoint:** `GET /documents/`
- **Method:** `GET`
- **Description:** Lists all stored documents with optional filtering by file type.
- **Query Parameters:**
  - `skip` (optional, integer, default: 0): Number of documents to skip.
  - `limit` (optional, integer, default: 100): Maximum number of documents to return.
  - `file_type` (optional, string): Filter documents by file type.
- **Success Response:**
  - **Code:** 200 OK
  - **Content:**
    ```json
    {
      "documents": [
        {
          "id": 1,
          "filename": "oracle_cards_by_deck.md",
          "file_type": "oracle_cards",
          "content_hash": "f26837c72c2586d180ac94a60821030a7e062f93c9cff61bee9c88dfe6af87a0",
          "content_length": 391714,
          "created_at": "2025-09-03T19:06:22.722505",
          "updated_at": "2025-09-03T19:06:22.722513"
        }
      ],
      "total": 1
    }
    ```

---

### 7. Get Document by ID

Retrieves a specific document by its unique ID, including the full content.

- **Endpoint:** `GET /documents/{document_id}`
- **Method:** `GET`
- **Description:** Fetches a complete document including its content and metadata.
- **Path Parameters:**
  - `document_id` (required, integer): The ID of the document to retrieve.
- **Success Response:**
  - **Code:** 200 OK
  - **Content:**
    ```json
    {
      "id": 1,
      "filename": "oracle_cards_by_deck.md",
      "file_type": "oracle_cards",
      "content_hash": "f26837c72c2586d180ac94a60821030a7e062f93c9cff61bee9c88dfe6af87a0",
      "content": "# Deck: lightFromNorthStock\n\n## Alternative route\n\nBe open to a different approach...",
      "content_length": 391714,
      "created_at": "2025-09-03T19:06:22.722505",
      "updated_at": "2025-09-03T19:06:22.722513"
    }
    ```
- **Error Response:**
  - **Code:** 404 Not Found
    - **Content:** `{"detail": "Document not found"}`

---

### 8. Delete Document

Removes a document from the database by its ID.

- **Endpoint:** `DELETE /documents/{document_id}`
- **Method:** `DELETE`
- **Description:** Permanently deletes a document from the database.
- **Path Parameters:**
  - `document_id` (required, integer): The ID of the document to delete.
- **Success Response:**
  - **Code:** 200 OK
  - **Content:** `{"message": "Document 'filename.md' deleted successfully"}`
- **Error Response:**
  - **Code:** 404 Not Found
    - **Content:** `{"detail": "Document not found"}`

---

## Document Storage Features

### Content-Addressable Storage
- All documents are stored with SHA-256 content hashing
- Automatic deduplication based on content hash
- Data integrity verification through hash comparison

### Search Methods
The system supports multiple search methods for retrieving documents:
1. **By file_type**: Semantic identifier (e.g., "oracle_cards", "two_card_readings")
2. **By filename**: Original filename for reference
3. **By content_hash**: Direct hash lookup for exact content matching

### File Validation
- Only `.md` files are accepted
- UTF-8 encoding validation
- Automatic content length calculation

### Update Behavior
- Uploading a file with the same filename updates the existing record
- Uploading a file with the same content hash updates the existing record
- New files are created for unique content

---

## Example Usage

### Upload a new oracle deck
```bash
curl -X POST "http://localhost:8000/documents/" \
  -F "file=@my_oracle_deck.md" \
  -F "file_type=oracle_cards"
```

### List all documents
```bash
curl -X GET "http://localhost:8000/documents/"
```

### Get a specific document
```bash
curl -X GET "http://localhost:8000/documents/1"
```

### Filter documents by type
```bash
curl -X GET "http://localhost:8000/documents/?file_type=oracle_cards"
```

### Delete a document
```bash
curl -X DELETE "http://localhost:8000/documents/1"
```
