# Architecture

## MVP Flow

```text
Vue UI
  -> Tauri shell
  -> FastAPI
  -> Embedding pipeline
  -> Qdrant search
  -> Optional LLM generation
```

## API Boundaries

- `/api/notes` owns note CRUD.
- `/api/ingest` coordinates parse, classify, embed, and store.
- `/api/chat` retrieves context and later generates answers.
- `/api/classify` is the TensorFlow-facing classification boundary.

The MVP should start with note CRUD and add embeddings only after the UI and API contract are stable.
