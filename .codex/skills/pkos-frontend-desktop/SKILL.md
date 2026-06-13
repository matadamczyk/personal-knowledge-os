---
name: pkos-frontend-desktop
description: Use for Vue 3, Tauri, Tailwind, Pinia, and desktop UI work in the Personal Knowledge OS app.
---

# Personal Knowledge OS Frontend Desktop

Use this skill when changing `apps/desktop`.

## Conventions

- Vue 3 with `<script setup lang="ts">`.
- Pinia for state that crosses components.
- Tailwind for styling.
- Shared API types should come from `packages/shared`.

## UI Direction

- Build the actual tool surface first.
- Keep operational screens dense, clear, and quiet.
- Do not add a landing page unless specifically requested.
- Avoid decorative UI that does not support the workflow.

## Quality

After frontend edits:

```sh
npm run format
npm run lint
npm run typecheck
```
