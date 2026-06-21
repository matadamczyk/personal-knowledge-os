---
name: pkos-quality-gate
description: Use before finishing development tasks in Personal Knowledge OS, especially after editing TypeScript, Vue, Python, YAML, JSON, Markdown, or config files.
---

# Personal Knowledge OS Quality Gate

Use this skill before handing back code changes.

## Required Commands

```sh
npm run format
npm run lint
npm run typecheck
```

For a single final command:

```sh
npm run check
```

## Tooling

- Prettier formats TypeScript, Vue, CSS, JSON, YAML, and Markdown.
- Ruff formats and lints Python.
- ESLint lints TypeScript and Vue.
- `vue-tsc` and `tsc` handle TypeScript typechecks.

## If A Command Fails

Fix deterministic formatter/linter failures first. Report remaining failures only when they require a product decision or missing external service.
