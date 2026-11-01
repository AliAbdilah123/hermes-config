---
name: source-app-setup
description: Install and verify applications from source repositories, especially Node monorepos and local web/desktop apps. Use when cloning, satisfying pinned toolchains, installing dependencies, launching services, or configuring a preferred local runtime/provider.
---

# Source Application Setup

Install from the repository's declared contract, then prove the app works.

## Workflow

1. **Read before installing.** Inspect the root README/quickstart, package manifest, lockfile, and repository agent/contributor instructions. Prefer the documented production or container path unless the user specifically needs development mode.
2. **Check prerequisites together.** Report OS/architecture, required runtime versions, package manager, container availability, and required companion CLIs in one probe.
3. **Honor exact pins.** Use the runtime range and package-manager version declared by the repository. Do not let an unrelated globally installed package manager silently override the project pin.
4. **Match binary architecture.** Derive the download target from `uname -m` before fetching an archive (`x86_64` → x64, `aarch64`/`arm64` → arm64). Verify the published checksum before extraction.
5. **Keep installation local when practical.** Prefer a user-owned toolchain directory and a scoped `PATH` over replacing system runtimes.
6. **Install dependencies using the lockfile.** Use frozen/immutable mode when supported. Long installs may run as a tracked background process with completion notification.
7. **Configure preferences only through supported state.** For a preferred agent/provider/runtime, first confirm its executable is on the service's effective `PATH`; then use the application's CLI, settings API, or UI after startup. Do not patch source merely to change a user preference.
8. **Verify end to end.** Start via the repository's documented lifecycle command, check health/status and logs, open or query the actual app, confirm the preferred integration is detected and selected, then report the URL and stop/start commands.

## Pitfalls

- A successful clone is not an installation.
- Do not claim completion while dependency installation or startup is still running.
- Do not infer CPU architecture from an existing Node binary or cloud host name.
- `corepack pnpm --version` may expose a global/default version; verify the project-requested version in the same environment used for installation.
- A CLI visible in an interactive shell may be absent from a GUI, container, daemon, or background service `PATH`.
- “Supported” and “default” are separate checks: detect the integration, then verify persisted selection.

## Completion evidence

Return only concrete evidence: installed path, versions, health/status result, reachable URL, selected runtime/provider, and concise lifecycle commands. If blocked, state the exact failed check and the next safe action.

Session-specific OpenDesign notes live in `references/open-design.md`.
