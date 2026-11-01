---
name: local-source-app-setup
description: Install, configure, launch, and verify a locally hosted application from a source repository. Use when a user asks to install or run a GitHub project, especially Node/pnpm monorepos with managed background services.
---

# Local Source Application Setup

Install from source all the way to a verified running artifact. Do not stop after cloning or dependency installation.

## Workflow

1. **Read repository guidance first**
   - Inspect `README.md`, quickstart/contributing docs, root `AGENTS.md`, package metadata, and lockfiles.
   - Prefer the repository's documented lifecycle command over guessed aliases.

2. **Inspect the host before changing it**
   - Check CPU architecture, required runtime versions, package manager, service manager/container runtime, and required companion CLIs.
   - Reuse compatible installed tools. Install only the missing runtime required by the project.

3. **Clone minimally**
   - Use `git clone --depth 1` unless history is required.
   - For large clones, run as a bounded background process with completion notification.
   - Verify the checkout exists before continuing after a timeout.

4. **Match pinned versions exactly**
   - Honor `engines`, `packageManager`, and lockfiles.
   - When downloading a runtime archive, derive the artifact suffix from `uname -m` (`x86_64` → `x64`, `aarch64` → `arm64`) and verify its checksum before extraction.
   - Put an app-specific runtime in a user-local directory and prepend it to `PATH`; avoid replacing the host runtime unnecessarily.

5. **Install and build**
   - Use the pinned package manager and frozen lockfile.
   - Treat successful postinstall/build output as installation evidence, but inspect build-script warnings for features the user actually needs.

6. **Launch through the supported lifecycle**
   - Use the repository's process manager/lifecycle command, not shell `&`, `nohup`, or an invented start command.
   - Choose explicit ports when defaults may collide.

7. **Configure through the product boundary**
   - Prefer a documented settings API or CLI over editing generated files or source defaults.
   - Update only the requested field so existing preferences and secrets are preserved.
   - Read the setting back after writing it.

8. **Verify the real result**
   - Probe the health endpoint.
   - Check lifecycle status and process logs.
   - Query runtime/provider discovery and confirm the requested executable is available at the expected path.
   - Fetch the web endpoint or use browser verification when practical. A healthy backend alone does not prove the UI is ready; first-load compilation may require extra time.

## Retry pattern

- If a full clone times out, check whether `.git` is valid; otherwise retry with `--depth 1` in the background.
- If a downloaded executable returns `Exec format error`, re-check `uname -m`, replace the archive with the matching architecture, and rerun version checks.
- If the web endpoint stalls while logs show initial compilation, wait for compilation and probe again rather than declaring failure.

## Completion report

Report only verified facts: install path, service URL, health/status result, selected default integration, and any unresolved warning affecting requested functionality.

See `references/node-pnpm-monorepo.md` for a compact verified recipe and probes.