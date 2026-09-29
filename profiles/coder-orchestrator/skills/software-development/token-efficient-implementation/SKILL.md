---
name: token-efficient-implementation
description: Deliver coding tasks with minimal conversational and tool-token overhead while preserving implementation, verification, and safety requirements. Use when the user asks for fewer tokens, terse execution, minimal narration, or a shortest-path implementation.
---

# Token-Efficient Implementation

Minimize overhead, not correctness.

## Execution loop

1. Read the direct specification and only the files needed to identify the owning code path.
2. Load the narrowest applicable procedural skill; avoid broad references unless a concrete boundary requires them.
3. Batch independent reads and inspections.
4. Prefer existing helpers, platform features, stdlib, and the smallest coherent diff.
5. Run focused RED→GREEN checks, then the proportionate canonical verification.
6. Continue through implementation and verification without progress-only final messages.
7. Report only a blocker requiring user action, or the finished artifact with concise evidence.

## Communication budget

- One short kickoff only when useful.
- Do not restate a supplied plan.
- Do not narrate routine phase transitions or repeat status already visible in tooling.
- A background-worker failure is not a user-facing stopping point when direct implementation can continue.
- Keep the final to artifact/link, verification, commit, and push when those boundaries were requested.

## Non-negotiable boundaries

Token reduction never removes input validation, authorization, data-loss prevention, accessibility, required tests, authenticated public E2E, or honest blocker reporting.

## Pitfalls

- Loading several large overlapping skills for a narrow edit.
- Sending `WORKING` as a final response while executable work remains.
- Repeating tool errors instead of silently taking the documented fallback.
- Treating fewer words as permission to skip fresh verification.
