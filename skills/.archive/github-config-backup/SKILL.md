---
name: github-config-backup
description: "Back up a local config directory (e.g. ~/.hermes) to a GitHub repo: survey files, write a safety-first .gitignore, init git, create an initial commit, and optionally schedule periodic push via cron."
tags: [backup, github, gitignore, cron, config-management]
related_skills: [git-project-setup, github-repo-management]
---

# GitHub Config Backup

## When to use
- User asks to back up `~/.hermes`, `~/.config`, or any local config directory to GitHub
- User wants a `.gitignore` that excludes secrets, runtime files, logs, caches, and vendored code
- User wants periodic automated backups (cron-driven)

## Workflow

### 1. Survey the target directory
Before writing `.gitignore`, map the directory:
- `find <dir> -maxdepth 2 -type f` to see top-level files
- `find <dir> -maxdepth 2 -type d` to see top-level directories
- Identify secret files (`.env`, `auth.json`, `*.lock`, `*.db`, `*.key`, `*.token`)
- Identify runtime artefacts (logs, caches, `node_modules`, `venv`, downloaded vendored paths)
- Check for **nested git repos** — these must be excluded or the outer repo will balloon in size
- Look for **large vendored/downloaded subtrees** inside profile-specific dirs (e.g. `profiles/*/home/go/pkg/mod/…`)

### 2. Write a layered `.gitignore`
Use a structured `.gitignore` at `<dir>/.gitignore` with these layers:

```gitignore
# Secrets / tokens / auth
.env
auth.json
auth.lock
shared/nous_auth.json
shared/nous_auth.lock
*.secret *.token *.key *.pem

# Databases / state
*.db *.db-wal *.db-shm
state.db* kanban.db*

# Locks
*.lock

# Runtime JSON state (non-config)
gateway_state.json gateway.lock processes.json
discord_threads.json channel_directory.json
*.prompt_snapshot.json .skills_prompt_snapshot.json

# Runtime artefacts
.hermes_history gateway.pid .update_check interrupt_debug.log

# Logs
**/*.log **/*.diag.log logs/ **/logs/

# Sessions (private history)
sessions/ **/sessions/

# Caches
cache/ audio_cache/ image_cache/ *.cache
context_length_cache.yaml provider_models_cache.json
models_dev_cache.json ollama_cloud_models_cache.json
*.recommended_cache.json *.openrouter_model_metadata.json

# Downloaded / compiled / vendored
bin/ node/ lsp/node_modules/ **/node_modules/ **/venv/
package-lock.json uv.lock flake.lock *.lock

# Large runtime dirs
home/ sandboxes/ pairing/
profiles/*/home/ profiles/*/sandboxes/ profiles/*/pairing/
profiles/*/cache/ profiles/*/lsp/node_modules/ profiles/*/bin/
profiles/*/state.db* profiles/*/gateway.lock profiles/*/.env
profiles/*/auth.json profiles/*/auth.lock
profiles/*/cron/.tick.lock profiles/*/cron/.jobs.lock
profiles/*/gateway_state.json profiles/*/discord_threads.json
profiles/*/processes.json profiles/*/models_dev_cache.json
profiles/*/channel_directory.json profiles/*/.skills_prompt_snapshot.json

# Nested agent source tree (tracked separately)
hermes-agent/

# Cron runtime
cron/.tick.lock cron/.jobs.lock cron/output/

# Plan artifacts
*.bak.*

# OS / editor junk
.DS_Store Thumbs.db *.swp *.swo *~ .~*
```

**Pitfalls:**
- Always check for nested git repos (`find <dir> -name .git -type d`) and exclude them.
- Watch for vendor paths that look like normal files but are actually huge (`profiles/*/home/go/pkg/mod/…`).
- After writing `.gitignore`, run `git status --short` and verify no secrets or caches appear staged.
- If a commit times out due to file count, use a longer `timeout` (120s+) or commit in batches.

### 3. Initialize and commit
```bash
cd <dir>
git init -q
git checkout -b main
git add -A
git commit -m "chore: initial config backup"
```

### 4. Create backup script
Place at `<dir>/scripts/backup-to-github.sh` (or copy from `templates/backup-script.sh`):

```bash
#!/usr/bin/env bash
set -euo pipefail
```
git config user.email "backup@local"
git config user.name "hermes-backup"
git add -A
if git diff --cached --quiet; then
  echo "Nothing to commit."
  exit 0
fi
git commit -m "backup: $(date '+%Y-%m-%d %H:%M:%S')"
if git remote get-url origin >/dev/null 2>&1; then
  git push origin main
else
  echo "No remote 'origin' configured."
fi
```

Make it executable: `chmod +x <dir>/scripts/backup-to-github.sh`

### 5. Schedule periodic push (optional)
Use Hermes `cronjob` or system cron:
```yaml
# Hermes cron
schedule: "0 2 * * *"
prompt: "Run bash <dir>/scripts/backup-to-github.sh and report stdout."
```

### 6. User one-time setup
Tell the user to create a GitHub repo and add the remote:
```bash
git remote add origin git@github.com:<user>/<repo>.git
git push -u origin main
```

## Pitfalls
- **Nested git repos**: If `<dir>` contains a subdirectory that is itself a git repo (e.g. `hermes-agent/`), the outer repo will track the inner `.git` folder as a regular directory. Exclude the nested repo entirely.
- **Vendored module caches**: Language package caches inside nested paths can be hundreds of megabytes. Always `find` for `node_modules`, `.venv`, `go/pkg/mod`, etc.
- **Commit timeouts**: Large initial commits with 100k+ files can exceed default 30s timeout. Use `timeout=120` in terminal calls.
- **Secret leakage**: Even with `.gitignore`, double-check `git status --short` before the first commit. Verify `config.yaml` does not contain live API keys; if it does, redact before committing.

## References
- `references/hermes-gitignore-template.md` — validated `.gitignore` for `~/.hermes`
- `templates/backup-script.sh` — reusable backup script
