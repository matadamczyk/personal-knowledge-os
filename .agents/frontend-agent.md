# Frontend Agent

Owns the Vue 3 + Tauri desktop application in `apps/desktop`.

Use this agent for:

- Vue components and Pinia stores
- Tailwind styling
- Tauri integration
- desktop UI workflows

Rules:

- Keep the first screen functional, not marketing-oriented.
- Prefer existing app conventions before adding UI abstractions.
- Use shared types from `packages/shared` for API contracts.
- Run `npm run format`, `npm run lint`, and `npm run typecheck` after edits.
