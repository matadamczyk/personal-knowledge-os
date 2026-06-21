---
name: pkos-dev-workflow
description: Use for development work in the Personal Knowledge OS repo, including monorepo structure, local commands, and the required final quality gate.
---

# Personal Knowledge OS Development Workflow

Use this skill for general work in this repo.

## Repo Map

- `apps/desktop` - Vue 3 + Tauri desktop app.
- `apps/api` - FastAPI backend.
- `packages/shared` - shared TypeScript types.
- `services/embeddings` - future embedding boundary.
- `services/ml` - future TensorFlow training boundary.
- `infra/docker` - local infrastructure.

## Default Workflow

1. Read the relevant local files before editing.
2. Keep changes scoped to the requested feature.
3. After edits, run `npm run format`.
4. Run `npm run lint`.
5. Run `npm run typecheck`.
6. For a final gate, run `npm run check`.

## Python Environment

Use Conda:

```sh
conda activate pkos-api
```

The root npm scripts call Python tools through `conda run -n pkos-api`.

## Avoid For Now

- Kubernetes.
- Redis/Celery.
- OAuth.
- local LLM hosting.
- early knowledge graph abstractions.
