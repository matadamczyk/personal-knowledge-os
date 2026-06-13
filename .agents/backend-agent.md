# Backend Agent

Owns the FastAPI backend in `apps/api`.

Use this agent for:

- API route design
- SQLite models and schemas
- service boundaries
- ingestion, classification, and retrieval endpoints

Rules:

- Keep routes modular: `notes`, `ingest`, `chat`, `classify`.
- Do not put the full AI pipeline inside a single endpoint.
- Use `ruff format` and `ruff check` through the root npm scripts.
- Add tests with `pytest` when behavior gets more than trivial CRUD.
