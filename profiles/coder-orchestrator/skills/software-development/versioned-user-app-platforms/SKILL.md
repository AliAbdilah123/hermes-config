---
name: versioned-user-app-platforms
description: Plan and implement authenticated platforms where users author tool-like apps, save drafts, publish immutable versions, distribute them through a marketplace, install them, and execute features safely.
---

# Versioned User-App Platforms

Use this for Studio/app-builder/extension-marketplace features that combine authentication, mutable drafts, immutable releases, installation, and prompt-backed execution.

Read [the architecture and planning reference](references/architecture.md) before designing the data model or API.

## Core workflow

1. Inspect the existing backend, data store, routes, frontend shell, tests, deployment path, and repository instructions.
2. Define ambiguous product verbs—Save, Publish, Install, Use—before naming tables or screens.
3. Separate mutable authoring state from immutable published snapshots.
4. Make publish a single transaction that saves the submitted draft and creates exactly one next version.
5. Enforce authentication and ownership in server-side queries.
6. Define the runtime trust boundary: supported schemas, input validation, prompt composition, output validation, provider/tool access, and run audit.
7. If approval precedes implementation, produce separate linked plan and visual-design review pages with an explicit implementation gate.
8. Verify authorization, version immutability, release sequencing, persistence, fresh build/restart, and public E2E before declaring ready.

## MVP discipline

Default to raw JSON schema editing, a documented schema subset, one existing model/provider path, pinned installations, and no unpublish. Ask for product decisions where these defaults materially change user expectations. Defer ratings, payments, moderation, collaboration, OAuth/SSO, visual schema builders, arbitrary JSON Schema, and per-app provider selection until required.

## Non-negotiable invariants

- Save never publishes.
- Publish always saves the exact submitted state and creates one immutable version.
- Marketplace reads snapshots, never drafts.
- Old versions survive later edits and feature deletion.
- Installed execution uses a published version, not mutable authoring rows.
- Schemas and inputs are validated server-side.
- Authored prompts cannot grant themselves credentials or arbitrary tools.
