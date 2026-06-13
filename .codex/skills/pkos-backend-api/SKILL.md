---
name: pkos-backend-api
description: Use for FastAPI backend work in Personal Knowledge OS, including routes, schemas, SQLAlchemy models, SQLite persistence, and future AI service boundaries.
---

# Personal Knowledge OS Backend API

Use this skill when changing `apps/api`.

## Conventions

- Keep route modules under `apps/api/app/api`.
- Keep SQLAlchemy models under `apps/api/app/models`.
- Keep Pydantic schemas under `apps/api/app/schemas`.
- Keep integration logic under `apps/api/app/services`.

## Route Boundaries

- `/api/notes` owns note CRUD.
- `/api/ingest` will coordinate parse, classify, embed, and store.
- `/api/chat` will retrieve context and later generate answers.
- `/api/classify` is the TensorFlow-facing classification boundary.

## Quality

After backend edits:

```sh
npm run format
npm run lint
```

Add `pytest` tests when backend behavior has branching, persistence edge cases, or external integrations.
