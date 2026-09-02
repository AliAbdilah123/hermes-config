# SPA subpath routing: build base and router basename

A nested SPA can serve its JS/CSS correctly yet still break after navigation when the bundler emits a subpath asset base but the history router remains rooted at `/`.

## Required contract

1. Build with the exact public prefix, including trailing slash (for example, Vite `--base=/projects/example/`).
2. Configure the history router with the same prefix, trimming only the trailing slash. Prefer deriving it from the bundler runtime base rather than duplicating a literal.
3. Ensure the framework's environment types are loaded when TypeScript does not recognize the bundler runtime environment (for Vite, `/// <reference types="vite/client" />`).
4. Inspect emitted HTML and require all entry JS/CSS URLs to begin with the public prefix.
5. Publicly verify both:
   - direct navigation to a nested route under the prefix;
   - in-app navigation/role switching, asserting the resulting URL remains under the prefix.

Asset HTTP 200 and correct MIME types do not prove router correctness.

## Verification-shell pitfall

Do not let deployment mask a failed verifier. A shape such as `verifier; rsync ...` can exit zero if the verifier fails but `rsync` succeeds. Use outer `set -euo pipefail` (not only inside the temporary verifier), or run verification and deployment as separate commands. Publish only after the verifier returns zero.
