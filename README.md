# Personal Knowledge OS

Monorepo for a desktop-first personal knowledge system.

## Structure

- `apps/desktop` - Vue 3 + Tauri desktop app
- `apps/api` - FastAPI backend
- `services/ml` - TensorFlow experiments and model training
- `services/embeddings` - embedding and vector-search service boundary
- `packages/shared` - shared TypeScript types and utilities
- `infra/docker` - local infrastructure
- `data` - local development data
- `docs` - architecture notes

## Setup

Install JavaScript dependencies:

```sh
npm install
```

Create the Python API environment with Conda:

```sh
cd apps/api
conda env create -f environment.yml
conda activate pkos-api
```

AI packages like `sentence-transformers`, `qdrant-client`, and `tensorflow` should be added to `apps/api/environment.yml` only when those features are being implemented.

Run Qdrant:

```sh
docker compose -f infra/docker/docker-compose.yml up -d qdrant
```

Run the API:

```sh
cd apps/api
conda activate pkos-api
uvicorn app.main:app --reload
```

Run the desktop UI in browser mode:

```sh
npm run dev:desktop
```

Run the Tauri desktop shell:

```sh
npm run dev:tauri
```
