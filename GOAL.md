# Personal Knowledge OS

## Vision

Personal Knowledge OS is a privacy-first desktop application that serves as a centralized knowledge management and intelligence platform for software engineers and technical professionals.

The application combines note-taking, document management, semantic search, AI-assisted knowledge retrieval, custom machine learning models, and knowledge graph visualization into a single desktop environment.

The long-term goal is to create a personal "second brain" capable of understanding, organizing, classifying, retrieving, and reasoning over the user's accumulated knowledge.

The system should become a daily-use productivity tool rather than a portfolio-only project.

---

# Core Objectives

The system must:

- Store personal knowledge in a structured format.
- Support notes, documents, code snippets, links, and AI conversations.
- Automatically classify and tag content using a custom TensorFlow model.
- Provide semantic search through embeddings and vector search.
- Support conversational interaction with the knowledge base using Retrieval-Augmented Generation (RAG).
- Visualize relationships between concepts and documents through a knowledge graph.
- Operate locally whenever possible.
- Minimize external API costs through local Small Language Models (SLMs).
- Be designed with extensibility and modularity in mind.

---

# Target Users

Primary user:

- The developer building this project.

Secondary users:

- Software engineers.
- AI engineers.
- Researchers.
- Technical writers.
- Knowledge workers.

---

# Technical Stack

## Desktop

- Tauri v2
- Vue 3
- TypeScript
- Pinia
- Vue Router
- Tailwind CSS

---

## Backend

- FastAPI
- SQLAlchemy
- Pydantic
- Alembic

---

## Database

Initial:

- SQLite

Production-ready:

- PostgreSQL

---

## Vector Database

- Qdrant

Responsibilities:

- Embedding storage
- Similarity search
- Retrieval for RAG

---

## AI Layer

### Embeddings

Examples:

- BGE-small
- BGE-base
- E5-small
- Sentence Transformers

Responsibilities:

- Semantic search
- RAG retrieval
- Similarity scoring

---

### Local Language Models

Primary runtime:

- Ollama

Candidate models:

- Phi-4 Mini
- Qwen 3
- Gemma 3
- Mistral Small

Responsibilities:

- Summaries
- Content enrichment
- Question answering
- Note generation

---

### TensorFlow Layer

Custom TensorFlow models are a mandatory part of the architecture.

TensorFlow must not be included only for demonstration purposes.

Models should solve actual product problems.

---

# TensorFlow Module

## Knowledge Classification Model

Purpose:

Automatically classify incoming knowledge into predefined categories.

Examples:

- FastAPI
- Python
- Vue
- DevOps
- Machine Learning
- System Design
- Bug Fix
- Research
- Personal
- Business Ideas

Input:

- Text embedding
- Metadata

Output:

- Category
- Confidence score

Example:

{
"category": "Machine Learning",
"confidence": 0.94
}

---

## Future TensorFlow Models

Potential roadmap:

### Topic Detection

Detect dominant themes within the knowledge base.

---

### Recommendation Engine

Recommend:

- related notes
- related projects
- relevant documents

---

### Knowledge Gap Analysis

Detect areas of interest that lack supporting information.

Example:

The user has extensive FastAPI knowledge but few DevOps notes.

---

### Personal Learning Model

Predict:

- areas of active learning
- declining topics
- future interests

---

# Functional Requirements

## Notes Module

Support:

- Markdown
- Tags
- Categories
- Attachments

Features:

- CRUD operations
- Full-text search
- Semantic search
- AI-generated summaries

---

## Document Module

Supported formats:

- PDF
- Markdown
- TXT
- DOCX

Features:

- Metadata extraction
- OCR-ready architecture
- Chunking pipeline
- Embedding generation

---

## Knowledge Search

Must support:

### Traditional Search

Keyword-based.

### Semantic Search

Embedding similarity.

### Hybrid Search

Keyword + semantic ranking.

---

## Chat Module

Users should be able to ask questions about their knowledge base.

Examples:

"What notes do I have about FastAPI authentication?"

"Show previous solutions for Docker issues."

"Summarize all Redis-related documents."

---

# Knowledge Graph

The system should maintain relationships between entities.

Examples:

FastAPI
↓
JWT
↓
Authentication

Project X
↓
Redis
↓
Caching

Requirements:

- Interactive visualization
- Relationship exploration
- Expandable graph structure

---

# AI Pipeline

Ingestion pipeline:

Content
↓
Classification
↓
Tagging
↓
Chunking
↓
Embedding
↓
Storage
↓
Graph Update

---

Chat pipeline:

Question
↓
Embedding
↓
Qdrant Search
↓
Context Retrieval
↓
SLM / LLM
↓
Response

---

# MVP Scope

Version 1 must include:

## Notes

- Create note
- Edit note
- Delete note
- List notes

## Search

- Keyword search
- Semantic search

## AI

- Embedding generation
- Qdrant integration

## Classification

- TensorFlow classification endpoint

## Desktop

- Tauri desktop application

---

# Non-Goals (MVP)

Do NOT implement:

- OAuth
- Multi-user support
- Cloud synchronization
- Kubernetes
- Distributed architecture
- Mobile applications
- Advanced analytics

These are future roadmap items.

---

# Architecture Principles

1. Offline-first whenever possible.
2. Privacy-first.
3. Modular AI architecture.
4. Local inference preferred.
5. API usage only for high-value operations.
6. Separation of concerns.
7. Production-grade code quality.
8. Testability.
9. Extensibility.
10. Long-term maintainability.

---

# Success Criteria

The project is considered successful when:

- It becomes the primary personal knowledge repository.
- New notes are automatically classified.
- Semantic search consistently retrieves relevant content.
- Chat can answer questions using personal knowledge.
- TensorFlow models operate in production workflows.
- The system is used multiple times per week.
- The architecture supports future expansion without major rewrites.

---

# Long-Term Vision

The final system should evolve into a personal operating system for knowledge:

- Knowledge storage
- Knowledge retrieval
- Knowledge classification
- Knowledge discovery
- Knowledge reasoning
- Knowledge visualization

## Obsidian & MCP Integration

To transition from a custom database to a "true" universal second brain, the system will support:

- **Direct Obsidian Vault Sync**: Storing and managing notes directly inside a local folder of plain Markdown `.md` files (compatible with Obsidian vaults).
- **AI-Powered Note Capture via Chat**: Intercepting conversational inputs in the AI chat to generate and write notes dynamically into the Obsidian vault.
- **Model Context Protocol (MCP) Server**: Turning the FastAPI backend into an MCP Server, exposing endpoints like note searching (`search_notes`), note creation (`create_note`), and text classification (`classify_text`) so that external editors (Claude Desktop, Cursor, etc.) can natively query and extend the user's knowledge vault.

## Multi-Provider LLM Switcher (Hybrid API / Local Runtime)

To mimic professional chatbots, the system will support flexible model routing:

- **Model Selector UI**: A frontend settings panel allowing users to toggle between local models (Ollama running Phi-4, Qwen, Gemma) and cloud providers (OpenAI GPT, Anthropic Claude, Gemini API).
- **Backend Model Abstraction Layer**: An unified API interface on the FastAPI backend that routes LLM prompts, summarizations, and chat completions based on the active provider selected by the user.

The application should function as a persistent memory layer augmenting the user's daily work and learning processes.
