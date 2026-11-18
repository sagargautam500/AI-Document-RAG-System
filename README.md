# AI Document RAG System

A conversational AI-powered document question-answering system built using **FastAPI, Google Gemini, Qdrant, PostgreSQL, and Redis**.

The system allows users to upload PDF and TXT documents, extract and process their content, generate vector embeddings, store document chunks in a vector database, and ask natural-language questions about the uploaded documents.

It also supports conversational memory using Redis and an LLM-powered interview booking workflow that collects user details and stores confirmed bookings in PostgreSQL.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Technology Stack](#technology-stack)
4. [System Architecture](#system-architecture)
5. [Project Structure](#project-structure)
6. [How It Works](#how-it-works)
7. [Installation and Setup](#installation-and-setup)
8. [Environment Configuration](#environment-configuration)
9. [Database Setup](#database-setup)
10. [Running the Application](#running-the-application)
11. [API Endpoints](#api-endpoints)
12. [API Testing](#api-testing)
13. [Database and Storage](#database-and-storage)
14. [Error Handling](#error-handling)
15. [Future Improvements](#future-improvements)

---

## Project Overview

The AI Document RAG System implements a custom Retrieval-Augmented Generation (RAG) pipeline.

Instead of relying entirely on an LLM's pretrained knowledge, the system retrieves relevant information from uploaded documents and provides that information as context to Google Gemini to generate answers.

The project also implements conversational memory, allowing users to maintain context across multiple messages within the same chat session.

Additionally, the system includes an interview booking feature that uses an LLM to detect booking intent, extract required details, ask for missing information, and save completed bookings in PostgreSQL.

### Main Objectives

- Build a document ingestion and processing pipeline.
- Implement multiple text chunking strategies.
- Generate semantic vector embeddings.
- Store and retrieve document chunks using a vector database.
- Develop a custom conversational RAG pipeline.
- Maintain chat history using Redis.
- Implement LLM-based interview booking.
- Store document metadata and interview bookings in PostgreSQL.

---

## Key Features

### 1. Document Ingestion

- Supports PDF and TXT document uploads.
- Extracts text from uploaded documents.
- Generates unique document identifiers.
- Processes documents into smaller text chunks.

### 2. Multiple Chunking Strategies

The system supports two chunking approaches:

**Fixed-Size Chunking**

Splits extracted text into chunks based on a predefined character size and overlap.

**Recursive Character Chunking**

Recursively splits text using different separators to preserve meaningful text boundaries whenever possible.

### 3. Embedding Generation

Uses the `sentence-transformers/all-MiniLM-L6-v2` model to generate semantic vector embeddings.

- Embedding dimension: 384
- Supports semantic similarity search.
- Uses normalized embeddings.

### 4. Vector Database Integration

Uses Qdrant for vector storage and similarity-based retrieval.

Each stored vector contains associated payload information, including:

- Document ID
- Filename
- Chunk ID
- Chunk text
- Chunking strategy

### 5. Metadata Storage

Uses PostgreSQL to store structured document metadata and interview booking information.

SQLAlchemy is used as the ORM.

### 6. Conversational RAG

Implements a custom RAG pipeline without using a prebuilt `RetrievalQAChain`.

The pipeline:

1. Receives a user's question.
2. Retrieves relevant document chunks.
3. Constructs contextual information.
4. Sends the question and context to Google Gemini.
5. Returns the generated answer and source information.

### 7. Redis Chat Memory

Uses Redis to maintain conversational history.

Features include:

- Session-based conversation storage.
- Retrieval of previous messages.
- Context-aware follow-up questions.
- Maintains the latest 10 messages per session.
- Automatic expiration after 24 hours.

### 8. LLM-Based Interview Booking

The system supports conversational interview booking.

It can:

- Detect interview booking intent.
- Extract the user's name.
- Extract the email address.
- Extract the preferred interview date.
- Extract the preferred interview time.
- Identify missing information.
- Ask follow-up questions.
- Save completed bookings in PostgreSQL.

---

## Technology Stack

| Category | Technology |
|---|---|
| Backend Framework | FastAPI |
| Programming Language | Python |
| LLM | Google Gemini |
| Embedding Model | Sentence Transformers |
| Embedding Model Name | all-MiniLM-L6-v2 |
| Vector Database | Qdrant |
| Relational Database | PostgreSQL |
| ORM | SQLAlchemy |
| Chat Memory | Redis |
| PDF Processing | PyMuPDF |
| API Documentation | Swagger UI |
| Data Validation | Pydantic |

---

## System Architecture

The project consists of three main workflows.

### 1. Document Ingestion Pipeline

```text
          User
           |
           v
     Upload PDF/TXT
           |
           v
      FastAPI API
           |
           v
    Text Extraction
           |
           v
     Text Chunking
           |
           v
   Embedding Generation
           |
           v
      Qdrant Storage
           |
           +----------------+
           |                |
           v                v
     Vector Chunks     PostgreSQL
                       Document Metadata
```

### 2. Conversational RAG Pipeline

```text
        User Question
              |
              v
          Chat API
              |
              v
       Retrieve Chat History
           (Redis)
              |
              v
      Contextual Query
              |
              v
      Semantic Retrieval
           (Qdrant)
              |
              v
      Relevant Document
           Chunks
              |
              v
       Google Gemini
              |
              v
       Generated Answer
              |
              v
       Save Chat History
           (Redis)
              |
              v
       Return Response
```

### 3. Interview Booking Pipeline

```text
        User Message
              |
              v
          Chat API
              |
              v
     Booking Intent Detection
              |
              v
     Extract Booking Details
              |
              v
      Check Missing Fields
              |
        +-----+-----+
        |           |
     Missing      Complete
        |           |
        v           v
   Ask Follow-up  Save Booking
    Question      PostgreSQL
        |           |
        v           v
   Redis Memory  Confirmation
```

---

## Project Structure

```text
ai-document-rag/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── documents.py
│   │   ├── retrieval.py
│   │   └── chat.py
│   │
│   ├── services/
│   │   ├── document_service.py
│   │   ├── chunking_service.py
│   │   ├── embedding_service.py
│   │   ├── qdrant_service.py
│   │   ├── metadata_service.py
│   │   ├── retrieval_service.py
│   │   ├── llm_service.py
│   │   ├── rag_service.py
│   │   ├── redis_service.py
│   │   ├── memory_service.py
│   │   └── booking_service.py
│   │
│   ├── database/
│   │   └── connection.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── document.py
│   │   └── interview_booking.py
│   │
│   └── schemas/
│       └── __init__.py
│
├── qdrant_storage/
│
├── .env
├── .gitignore
├── requirements.txt
│
├── create_tables.py
├── test_db.py
├── test_redis.py
├── test_memory.py
├── test_booking.py
├── test_booking_save.py
└── README.md
```

---

## How It Works

### Document Processing

When a user uploads a document:

1. FastAPI receives the uploaded file.
2. The document service extracts its text.
3. The chunking service divides the text using the selected strategy.
4. The embedding service converts each chunk into a 384-dimensional vector.
5. Qdrant stores the vectors and their payloads.
6. PostgreSQL stores the associated document metadata.

### Question Answering

When a user asks a question:

1. The chat API receives the question and session ID.
2. Redis retrieves the previous conversation history.
3. The system constructs a contextual search query.
4. Qdrant retrieves the most relevant document chunks.
5. The retrieved content is passed to Google Gemini.
6. Gemini generates a contextual answer.
7. The question and answer are saved in Redis.
8. The API returns the answer and source information.

### Interview Booking

When a user requests an interview booking:

1. Gemini detects the booking intent.
2. The booking service extracts available details.
3. The system checks whether any required fields are missing.
4. If information is missing, the API asks a follow-up question.
5. The conversation continues using the same session ID.
6. Once all required information is available, the booking is stored in PostgreSQL.
7. The API returns booking confirmation.

---

## Installation and Setup

### Prerequisites

Install the following before running the project:

- Python 3.12
- PostgreSQL
- Redis Cloud account or a Redis server
- Google Gemini API key
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/sagargautam500/AI-Document-RAG-System.git

cd ai-document-rag
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the virtual environment.

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory.

Add the required database, Gemini, and Redis configuration.

See the Environment Configuration section below.

### 5. Configure PostgreSQL

Create a PostgreSQL database named:

```sql
CREATE DATABASE ai_document_rag;
```

Update your database connection settings in the `.env` file according to `app/database/connection.py`.

### 6. Create Database Tables

Run:

```bash
python create_tables.py
```

This creates the required SQLAlchemy tables, including:

- `documents`
- `interview_bookings`

### 7. Configure Redis

Configure your Redis connection URL in `.env`.

The project uses Redis for session-based conversational memory.

### 8. Qdrant Storage

The project uses local persistent Qdrant storage.

The storage directory is:

```text
qdrant_storage/
```

The application creates and uses the `documents` collection with cosine similarity and 384-dimensional vectors.

---

## Environment Configuration

Example `.env` structure:

```env
GEMINI_API_KEY=your_gemini_api_key

REDIS_URL=your_redis_connection_url

# Add the PostgreSQL configuration
# using the exact variable names expected
# by app/database/connection.py.
```

**Important:**

- Never commit `.env` to GitHub.
- Never expose API keys or database passwords.
- Use `.env.example` to share the required variable names without actual secrets.

---

## Running the Application

Activate your virtual environment and run:

```bash
fastapi dev app/main.py
```

The API will be available at:

```text
http://127.0.0.1:8000
```

### Swagger API Documentation

Open:

```text
http://127.0.0.1:8000/docs
```

Swagger UI provides an interactive interface for testing the available API endpoints.

---

## API Endpoints

The project currently exposes the following main API endpoints.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/documents/upload` | Upload and process PDF/TXT documents |
| POST | `/api/v1/retrieval/search` | Search for semantically similar document chunks |
| POST | `/api/v1/chat/ask` | Conversational RAG and interview booking |

### 1. Document Upload

**Endpoint:**

```http
POST /api/v1/documents/upload
```

Supports PDF and TXT document uploads.

The upload workflow extracts text, applies the selected chunking strategy, generates embeddings, stores vectors in Qdrant, and saves metadata in PostgreSQL.

### 2. Semantic Retrieval

**Endpoint:**

```http
POST /api/v1/retrieval/search
```

Retrieves relevant document chunks using vector similarity search.

### 3. Conversational Chat

**Endpoint:**

```http
POST /api/v1/chat/ask
```

Example request:

```json
{
  "session_id": "rag-session-001",
  "question": "What are the technical skills mentioned in my resume?",
  "limit": 5
}
```

Example response structure:

```json
{
  "session_id": "rag-session-001",
  "type": "document_chat",
  "question": "What are the technical skills mentioned in my resume?",
  "answer": "Generated answer based on retrieved document content.",
  "sources": []
}
```

The actual `sources` array contains the retrieved source information when relevant chunks are found.

### Interview Booking Example

Use the same chat endpoint.

```json
{
  "session_id": "booking-session-001",
  "question": "I want to book an interview. My name is John Doe.",
  "limit": 5
}
```

The API identifies the booking intent and asks for any missing information.

The conversation should continue using the same `session_id` until all required booking details are collected.

---

## API Testing

The following components have been tested during development:

| Component | Testing |
|---|---|
| PostgreSQL Connection | Successful |
| Redis Connection | Successful |
| PDF Text Extraction | Successful |
| TXT Text Extraction | Successful |
| Fixed-Size Chunking | Successful |
| Recursive Character Chunking | Successful |
| Embedding Generation | Successful |
| Qdrant Vector Storage | Successful |
| Document Metadata Storage | Successful |
| Document Upload API | Successful |
| Semantic Retrieval API | Successful |
| Gemini RAG Response | Successful |
| Interview Intent Detection | Successful |
| Interview Detail Extraction | Successful |
| Booking Follow-up Questions | Successful |
| Interview Booking Storage | Successful |
| Normal RAG Chat | Successful |

---

## Database and Storage

### PostgreSQL

PostgreSQL stores structured application data.

Main tables:

**documents**

Stores uploaded document metadata.

**interview_bookings**

Stores confirmed interview booking details, including:

- Booking ID
- Session ID
- Name
- Email
- Interview date
- Interview time
- Created timestamp

### Qdrant

Qdrant stores vector embeddings and document chunk payloads.

Collection:

```text
documents
```

Vector configuration:

```text
Dimension: 384
Distance: Cosine
```

### Redis

Redis stores conversational history.

Key format:

```text
chat:{session_id}
```

Memory configuration:

```text
Maximum messages: 10
Expiration: 24 hours
```

---

## Error Handling

The API uses HTTP exceptions to return meaningful error responses.

Common error cases include:

- Empty user questions.
- Invalid input data.
- Missing or invalid document information.
- Database connection failures.
- Redis connection failures.
- External LLM API failures.

External Gemini API requests may occasionally return temporary service errors such as `503 UNAVAILABLE`. These errors indicate that the external model service is temporarily unavailable.

---

## Future Improvements

Potential improvements for future versions include:

- Better document-level filtering during retrieval.
- Improved chunking and retrieval strategies.
- More robust input validation.
- Duplicate interview booking prevention.
- Booking date and time validation.
- Improved LLM error handling and retry mechanisms.
- Automated unit and integration testing.
- Authentication and authorization.
- Document deletion and management APIs.
- Docker-based deployment.
- Production deployment and monitoring.

---

## Author

**Sagar Gautam**

BSc. CSIT Graduate | MSc. CSIT Student

GitHub: [sagargautam500](https://github.com/sagargautam500)

Portfolio: [sagargautam500.com.np](https://www.sagargautam500.com.np)

---

## License

This project was developed for educational and assignment purposes.

Add an appropriate open-source license if you intend to distribute the project publicly.
