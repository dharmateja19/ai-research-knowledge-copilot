# AI Research & Knowledge Copilot

An AI-powered research assistant that enables users to upload documents, ask questions conversationally, and receive document-grounded answers with source and page citations.

The system combines **RAG, hybrid retrieval, reranking, conversational memory, LangGraph-based routing, Redis caching, and WebSocket streaming** into a full-stack application.

---

## Features

- PDF document ingestion
- Intelligent document chunking
- Hugging Face sentence embeddings
- Semantic vector search using Qdrant
- Keyword-based retrieval
- Hybrid semantic + keyword retrieval
- Cross-Encoder reranking
- Retrieval-Augmented Generation (RAG)
- Source and page-level citations
- Evidence checking to reduce unsupported answers
- Conversational memory
- Conversation-specific document selection
- Redis response caching
- WebSocket-based response streaming
- LangGraph-based query routing
- React-based web interface
- PostgreSQL persistence
- Docker-based infrastructure

---

## System Architecture

```text
                    ┌─────────────────────┐
                    │      React UI       │
                    └──────────┬──────────┘
                               │
                     REST / WebSocket
                               │
                    ┌──────────▼──────────┐
                    │      FastAPI        │
                    │       Backend       │
                    └──────────┬──────────┘
                               │
                       ┌───────▼───────┐
                       │    Router     │
                       │   LangGraph   │
                       └───────┬───────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
             GENERAL                       RAG
                  │                         │
                  ▼                         ▼
             LLM Answer              Query Processing
                                            │
                                   ┌────────▼────────┐
                                   │ Hybrid Retrieval│
                                   └────────┬────────┘
                                            │
                              ┌─────────────┴─────────────┐
                              │                           │
                         Qdrant Search              Keyword Search
                              │                           │
                              └─────────────┬─────────────┘
                                            │
                                     ┌──────▼──────┐
                                     │  Reranker   │
                                     └──────┬──────┘
                                            │
                                     ┌──────▼──────┐
                                     │   Evidence  │
                                     │    Check    │
                                     └──────┬──────┘
                                            │
                                     ┌──────▼──────┐
                                     │     LLM     │
                                     │   Answer    │
                                     └──────┬──────┘
                                            │
                                     Citations + Answer
```

---

## RAG Pipeline

```text
PDF
 │
 ▼
Document Ingestion
 │
 ▼
Text Extraction
 │
 ▼
Chunking
 │
 ▼
Sentence Embeddings
 │
 ▼
Qdrant Vector Storage
 │
 ▼
User Question
 │
 ▼
Query Embedding
 │
 ├───────────────┐
 ▼               ▼
Semantic       Keyword
Search         Search
 │               │
 └───────┬───────┘
         ▼
  Hybrid Retrieval
         │
         ▼
 Cross-Encoder
   Reranking
         │
         ▼
Relevant Context
         │
         ▼
 Evidence Check
         │
         ▼
        LLM
         │
         ▼
Grounded Answer
 + Citations
```

---

## Query Routing

The application distinguishes between general/coding questions and document-based questions.

### General Query

```text
User Question
      │
      ▼
   Router
      │
   GENERAL
      │
      ▼
     LLM
      │
      ▼
   Answer
```

General questions are answered directly by the LLM without document citations.

### Document Query

```text
User Question
      │
      ▼
   Router
      │
      ▼
     RAG
      │
      ▼
Retrieve
      │
      ▼
Rerank
      │
      ▼
Evidence Check
      │
      ▼
Document-grounded Answer
      │
      ▼
Source + Page Citations
```

If the retrieved documents do not contain enough information, the system returns:

```text
The provided documents do not contain enough information to answer this question.
```

---

## Tech Stack

### Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- PostgreSQL
- Pydantic Settings

### AI / Machine Learning

- Hugging Face
- Sentence Transformers
- `all-MiniLM-L6-v2`
- Cross-Encoder
- `ms-marco-MiniLM-L-6-v2`
- Ollama
- Llama 3.2

### Retrieval

- Qdrant
- Semantic Search
- Keyword Search
- Hybrid Retrieval
- Cross-Encoder Reranking

### Agent / Workflow

- LangGraph
- Intent Routing
- Evidence Verification

### Frontend

- React.js
- Vite
- Tailwind CSS
- WebSocket API

### Infrastructure

- Docker
- Docker Compose
- Redis
- PostgreSQL

---

## Project Structure

```text
AI_RESEARCH_ASSISTANT/
│
├── app/
│   ├── agent.py
│   ├── conversation_service.py
│   ├── database.py
│   ├── keyword_search.py
│   ├── llm_service.py
│   ├── main.py
│   ├── models.py
│   ├── qdrant_service.py
│   ├── rag_service.py
│   ├── redis_service.py
│   ├── retrieval_service.py
│   └── tools.py
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── uploads/
│
├── docker-compose.yml
├── requirements.txt
├── index_document.py
│
├── test_agent.py
├── test_agent_routing.py
├── test_chunk_embeddings.py
├── test_conversation_documents.py
├── test_conversation_rag.py
├── test_document_filter.py
├── test_embeddings.py
├── test_hybrid_search.py
├── test_llm.py
├── test_memory.py
├── test_qdrant.py
├── test_rag.py
├── test_redis.py
├── test_reranker.py
├── test_search.py
├── test_tool.py
├── test_websocket.py
│
├── README.md
└── .gitignore
```

---

## Infrastructure

Docker Compose runs the following services:

| Service | Purpose | Port |
|---|---|---|
| PostgreSQL | Application database | `5434` |
| Qdrant | Vector database | `6333` |
| Redis | Response caching | `6379` |

The FastAPI backend runs on:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/dharmateja19/ai-research-knowledge-copilot
cd ai-research-knowledge-copilot
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

Activate on Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5434/research_copilot
```

Do not commit `.env` to GitHub.

### 5. Start infrastructure

```bash
docker compose up -d
```

Check running containers:

```bash
docker ps
```

### 6. Start Ollama

Make sure Ollama is installed and the required model is available:

```bash
ollama pull llama3.2
```

### 7. Start the backend

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

### 8. Start the frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

---

## Document Workflow

1. Upload a PDF through the React interface.
2. FastAPI extracts the document text.
3. The document is divided into smaller chunks.
4. Chunks are stored in PostgreSQL.
5. Embeddings are generated using Sentence Transformers.
6. Embeddings are stored in Qdrant.
7. Documents can be attached to conversations.
8. Questions are searched only against documents attached to the conversation.

---

## Retrieval Strategy

The application combines two retrieval approaches.

### Semantic Retrieval

The user's question is converted into an embedding and searched against Qdrant using vector similarity.

### Keyword Retrieval

The application also searches document chunks using keyword matching.

### Hybrid Retrieval

The results are combined using weighted scoring:

```text
Hybrid Score =
    0.7 × Semantic Score
  + 0.3 × Keyword Score
```

The resulting candidates are then passed through a Cross-Encoder reranker to select the most relevant chunks.

---

## Conversation Memory

Conversations and messages are persisted in PostgreSQL.

Each message stores:

```text
conversation_id
role
content
sources
created_at
```

This allows the application to:

- Continue conversations
- Resolve follow-up questions
- Preserve previous answers
- Preserve source citations after reopening a conversation

---

## Redis Caching

Redis is used to cache generated responses.

```text
User Question
      │
      ▼
 Redis Cache
   /      \
 HIT      MISS
 │          │
 ▼          ▼
Answer    RAG / LLM
             │
             ▼
         Store Result
             │
             ▼
          Response
```

The cache key considers:

- Conversation ID
- Question
- Attached document IDs
- Query route

---

## WebSocket Streaming

The application uses WebSockets for conversational responses.

Example message flow:

```text
Client
  │
  │ Question
  ▼
FastAPI WebSocket
  │
  ├── route
  ├── sources
  ├── token
  ├── token
  ├── token
  └── done
  │
  ▼
React UI
```

This allows the frontend to receive the answer progressively.

---

## LangGraph Workflow

LangGraph is used to control the query-processing workflow.

```text
                START
                  │
                  ▼
                Router
               /      \
              /        \
        GENERAL          RAG
           │              │
           ▼              ▼
          LLM       Knowledge Tool
           │              │
           │              ▼
           │       Evidence Check
           │          /       \
           │        YES        NO
           │         │          │
           │         ▼          ▼
           │      RAG Answer  Insufficient
           │         │          │
           └─────────┴──────────┘
                     │
                    END
```

The router identifies whether the query should be answered using the general LLM or the document knowledge base.

---

## Evidence Checking

For RAG queries, retrieved context is checked before generating the final answer.

```text
Retrieved Context
       │
       ▼
Evidence Checker
       │
   ┌───┴────┐
   │        │
  YES       NO
   │        │
   ▼        ▼
Generate   Reject
Answer     Unsupported
   │        │
   ▼        ▼
Citations  Insufficient
```

This helps prevent the system from generating document-grounded answers when the retrieved context does not contain sufficient evidence.

---

## Testing

The project includes tests for major components:

```text
test_agent.py
test_agent_routing.py
test_chunk_embeddings.py
test_conversation_documents.py
test_conversation_rag.py
test_document_filter.py
test_embeddings.py
test_hybrid_search.py
test_llm.py
test_memory.py
test_qdrant.py
test_rag.py
test_redis.py
test_reranker.py
test_search.py
test_tool.py
test_websocket.py
```

Run an individual test:

```bash
python test_rag.py
```

Test the LangGraph agent:

```bash
python test_agent.py
```

---

## Example Queries

### Document Question

```text
What is deep learning according to the uploaded document?
```

The system retrieves relevant document chunks and provides citations.

### Follow-up Question

```text
What are its main characteristics?
```

The conversation history is used to resolve the reference.

### General Question

```text
Write a Python program to reverse a string.
```

The query is routed to the general LLM and does not use document citations.

### Unsupported Document Question

```text
What is quantum computing according to the uploaded document?
```

If the document does not contain sufficient evidence:

```text
The provided documents do not contain enough information to answer this question.
```

---

## Current Capabilities

The current version can:

- Upload and process research PDFs
- Generate and store embeddings
- Search documents semantically
- Combine semantic and keyword retrieval
- Rerank retrieved results
- Generate document-grounded answers
- Cite source documents and pages
- Maintain conversational context
- Restrict retrieval to selected conversation documents
- Cache repeated queries using Redis
- Stream responses over WebSockets
- Route general and document-based questions
- Verify evidence before producing document-grounded answers
- Persist conversations and source citations

---

## Roadmap

### Completed

- [x] FastAPI backend
- [x] PostgreSQL persistence
- [x] PDF ingestion
- [x] Document chunking
- [x] Sentence embeddings
- [x] Qdrant vector search
- [x] Keyword search
- [x] Hybrid retrieval
- [x] Cross-Encoder reranking
- [x] RAG
- [x] Citation grounding
- [x] Conversation memory
- [x] Conversation-specific documents
- [x] Redis caching
- [x] WebSocket streaming
- [x] LangGraph routing
- [x] Evidence checking
- [x] React frontend

### Planned

- [ ] Agentic research planner
- [ ] Multi-step research workflow
- [ ] Research task execution
- [ ] Evidence aggregation and synthesis
- [ ] Citation validation
- [ ] Redis background job queue
- [ ] Authentication and authorization
- [ ] Production configuration
- [ ] Automated testing improvements
- [ ] CI/CD
- [ ] Cloud deployment
- [ ] Production documentation

---

## Future Architecture

The planned agentic research workflow will extend the existing RAG pipeline:

```text
                    User Question
                         │
                         ▼
                  Research Planner
                         │
                  ┌──────┴──────┐
                  │             │
             Research        General
               Tasks           Query
                  │             │
                  ▼             ▼
          Research Executor     LLM
                  │
          ┌───────┼────────┐
          ▼       ▼        ▼
       Search   Retrieve  Other Tools
          │       │        │
          └───────┼────────┘
                  ▼
           Evidence Collection
                  │
                  ▼
             Synthesizer
                  │
                  ▼
          Citation Validation
                  │
                  ▼
             Final Answer
```

---

## Author

**Dharma Teja Pamarthi**

B.Tech — Computer Science & Engineering (AI & ML)

---

## License

This project is intended for educational, portfolio, and research purposes.