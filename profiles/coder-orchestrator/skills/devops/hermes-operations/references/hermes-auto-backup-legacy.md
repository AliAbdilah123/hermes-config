# Legacy skill package: `hermes-auto-backup`

This file preserves the former `hermes-auto-backup` SKILL.md after consolidation into `hermes-operations`. Relative support-file links have been rewritten to the re-homed files under `hermes-operations`.

---

---
name: hermes-auto-backup
title: Hermes Config Auto Backup
description: Backup Hermes configuration to a Git remote on a schedule, with safe exclusions and verified push.
---

# Hermes Config Auto Backup

Use this skill when the user wants periodic GitHub backups of Hermes config, or when managing `~/.hermes_backup*` and related cron jobs.

## Trigger
- "backup hermes config to github"
- "schedule hermes backups"
- "regularly push ~/.hermes to github"
- "setup automatic config backup"

## Workflow
1. Choose/verify backup repo
2. Prepare a clean local staging repo under `~/.hermes-backups/`
3. Create or update `~/.hermes/scripts/hermes-auto-backup-backup-github.sh`
4. Run once manually to verify push
5. Create a Hermes cron job for recurring execution
6. Confirm job state and report commit/push status

## Safety rules
- Do NOT push runtime/state files by default:
  - `state.db`, `state.db-shm`, `state.db-wal`
  - `*.lock`, `gateway.pid`
  - `logs/`
  - `.env`, `.auth`
  - `node/`, `node_modules/`, `__pycache__/`, `*.pyc`, `*.pyo`
  - `.hermes_history`, `.skills_prompt_snapshot.json`
- Prefer SSH remote when authenticated: `git@github.com:<owner>/<repo>.git`
- The backup script must be idempotent and report: changed files count, commit hash, or "No changes to commit".

## Script contract
Path: `~/.hermes/scripts/hermes-auto-backup-backup-github.sh`
Behavior:
- Receives optional commit message arg, default `backup: update hermes config`
- Uses `rsync -a --delete` with exclusions listed above
- Commits only when `git diff --cached` is non-empty
- Pushes and prints status

## Cron contract
- Name: `hermes-config-backup`
- Schedule: typically `every 1h` unless user requests different
- Prompt: run the backup script and report changed files count, commit hash/"No changes", and push status
- Repeat: `forever`
- Deliver: `origin`
