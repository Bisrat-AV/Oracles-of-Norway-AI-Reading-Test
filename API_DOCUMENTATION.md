# Oracles of Norway AI Readings API Documentation

This document provides an overview of the API endpoints for the Oracles of Norway AI Readings service.

## Base URL

The API is served from the root of the application. When running locally, the base URL is:
`http://127.0.0.1:8000`

---

## Authentication

There is currently no authentication required to access this API.

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

### 4. Generate Oracle Reading

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
    "alpha": 0.5
  }
  ```
  - `deck_name` (required, string): The name of the deck from which the cards are drawn.
  - `card_names` (required, array of strings): A list of the names of the cards that were drawn.
  - `alpha` (optional, float, default: 0.5): A value between 0.0 and 1.0 to balance the hybrid search. `0.0` is pure keyword search, `1.0` is pure semantic search.
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
