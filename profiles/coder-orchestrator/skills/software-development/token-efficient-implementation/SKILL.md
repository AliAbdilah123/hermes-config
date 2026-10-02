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
- If live-provider evidence requires the user to resend/retry, first deploy and health-check the diagnostic or implementation, then ask once with the exact action. Do not request a resend before the relevant build is live; correlate callback and deployment timestamps to avoid redundant user loops.
- Keep the final to artifact/link, verification, commit, and push when those boundaries were requested.

## Non-negotiable boundaries

Token reduction never removes input validation, authorization, data-loss prevention, accessibility, required tests, authenticated public E2E, or honest blocker reporting.

## Live-provider evidence gates

For webhook/provider fixes that require observing an unknown callback shape:

1. Deploy only the privacy-safe diagnostic first and health-check that exact deployment.
2. Ask once for the provider action, then correlate callback and deployment timestamps.
3. Record only redacted structure/classifications—never raw payload values or URLs.
4. Convert the observed shape into a redacted fixture/test, support only that proven variant, and remove temporary diagnostics.
5. Deploy, then request one fresh callback to prove the deployed parser and authenticated rendered result. Stay below `READY` until both pass.

The discovery callback proves payload shape; the post-deployment callback proves the implementation. Explain this distinction in one sentence so the second request does not look redundant.

## Pitfalls

- Loading several large overlapping skills for a narrow edit.
- Sending `WORKING` as a final response while executable work remains.
- Repeating tool errors instead of silently taking the documented fallback.
- Treating fewer words as permission to skip fresh verification.
- Calling a provider-backed fix complete after local tests or the discovery callback.
