# OpenDesign source setup notes

Use these notes only after checking the repository's current documentation; upstream commands and versions can change.

## Observed repository contract

- Linux runs from source; the official desktop download may not provide a Linux artifact.
- The repository declares Node `~24` and a pinned pnpm 10.x version in `package.json`.
- Development lifecycle is managed through `pnpm tools-dev`; avoid inventing legacy `dev` or `start` aliases.
- A foreground web run starts daemon + web; managed background commands expose status, logs, restart, and stop operations.
- OpenDesign detects local agent CLIs from the daemon's effective `PATH`.
- Hermes is a supported local runtime and MCP target. Runtime detection alone does not prove Hermes is the selected default.

## Minimal verification sequence

1. Confirm Node and pnpm satisfy the current root manifest.
2. Install with the lockfile's frozen mode.
3. Confirm `hermes` resolves in the same environment that launches OpenDesign.
4. Start with the documented `tools-dev` lifecycle command.
5. Check managed status/health and recent logs.
6. In OpenDesign settings or its supported API/CLI, rescan local runtimes and select Hermes.
7. Restart, then verify Hermes remains selected and execute one small prompt through it.

## Architecture-safe Node fallback

When system Node is too old and no version manager exists, install a user-local official Node archive:

- Map `uname -m` before download: `x86_64` → `linux-x64`; `aarch64`/`arm64` → `linux-arm64`.
- Download the matching `SHASUMS256.txt` and archive from nodejs.org.
- Verify with `sha256sum -c` before extracting.
- Prepend the local `bin` directory only for OpenDesign install/start commands unless the user asks for a global default.

Do not preserve exact release numbers here; trust the current repository manifest.
