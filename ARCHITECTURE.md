# Personal Knowledge OS Architecture

## System Overview

Personal Knowledge OS is a desktop-first AI-powered knowledge management platform.

The architecture follows a modular design with clear separation between:

- User Interface
- Application Logic
- AI Services
- Data Storage
- Machine Learning

The system is designed to operate locally whenever possible.

---

# High Level Architecture

┌─────────────────────────────┐
│ Tauri Desktop │
├─────────────────────────────┤
│ Vue UI │
│ Pinia Store │
│ TailwindCSS │
└──────────────┬──────────────┘
│
▼
┌─────────────────────────────┐
│ FastAPI Backend │
├─────────────────────────────┤
│ Notes API │
│ Search API │
│ Chat API │
│ Classification API │
│ Ingestion API │
└───────┬───────────┬─────────┘
│ │
▼ ▼

┌─────────────┐ ┌─────────────┐
│ TensorFlow │ │ RAG Engine │
│ Models │ │ Retrieval │
└──────┬──────┘ └──────┬──────┘
│ │
▼ ▼

┌─────────────┐ ┌─────────────┐
│ PostgreSQL │ │ Qdrant │
│ Metadata │ │ Embeddings │
└─────────────┘ └─────────────┘

---

# Repository Structure

personal-knowledge-os/

apps/
├── desktop/
└── api/

services/
├── ml/
├── embeddings/

packages/
├── shared/

infra/
├── docker/

docs/

data/

---

# Frontend Layer

Location:

apps/desktop

Technology:

- Vue 3
- TypeScript
- Pinia
- Vue Router
- TailwindCSS
- Tauri

Responsibilities:

- UI rendering
- User interactions
- State management
- API communication

Frontend must contain no AI business logic.

All AI operations are executed through FastAPI.

---

# Backend Layer

Location:

apps/api

Technology:

- FastAPI
- SQLAlchemy
- Alembic
- Pydantic

Responsibilities:

- CRUD operations
- Search orchestration
- RAG orchestration
- Classification orchestration
- File ingestion

---

# AI Layer

Location:

services/

Submodules:

services/ml/
services/embeddings/

The AI layer is independent from the frontend.

All AI functionality must be callable through API endpoints.

---

# TensorFlow Service

Purpose:

Knowledge classification.

Responsibilities:

- Model loading
- Prediction
- Training pipeline
- Model versioning

Endpoints:

POST /classify

Response:

{
"category": "Machine Learning",
"confidence": 0.93
}

Future:

- recommendation engine
- topic detection
- knowledge gap detection

---

# Embedding Service

Responsibilities:

- embedding generation
- vector indexing
- semantic retrieval

Workflow:

Text
↓
Embedding Model
↓
Qdrant
↓
Search

---

# Storage Layer

## PostgreSQL

Stores:

- notes
- tags
- metadata
- document references
- relationships

Does NOT store embeddings.

---

## Qdrant

Stores:

- embeddings
- vector metadata

Used for:

- semantic search
- retrieval

---

# RAG Pipeline

Question
↓
Embedding
↓
Qdrant Search
↓
Top K Results
↓
Context Builder
↓
LLM / SLM
↓
Response

---

# Ingestion Pipeline

User Content
↓
Validation
↓
TensorFlow Classification
↓
Tag Generation
↓
Chunking
↓
Embedding Generation
↓
Qdrant Storage
↓
Metadata Storage

---

# Core Entities

## Note

id
title
content
summary
category
created_at
updated_at

---

## Document

id
filename
filetype
path
category

---

## Tag

id
name

---

## Conversation

id
title
created_at

---

## KnowledgeLink

source_id
target_id
relationship_type

---

# API Design

/api/v1

Endpoints:

GET /notes
POST /notes
PUT /notes/{id}
DELETE /notes/{id}

POST /search

POST /chat

POST /classify

POST /ingest

---

# Architectural Principles

1. Offline-first
2. Modular AI services
3. Privacy-first
4. Local inference preferred
5. API-first design
6. Separation of concerns
7. Testable components
8. Extensible architecture
9. Avoid premature optimization
10. Minimize external dependencies

---

# Future Architecture

Phase 2:

- GitHub ingestion
- PDF ingestion

Phase 3:

- Knowledge Graph

Phase 4:

- Local SLM integration

Phase 5:

- Recommendation engine

Phase 6:

- Multi-device synchronization
