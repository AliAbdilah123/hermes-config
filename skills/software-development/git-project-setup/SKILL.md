---
name: git-project-setup
description: "Initialize new Git projects with sensible defaults: .env* (secrets), .DS_Store (macOS), and standard first commit. Use whenever a user asks to create a fresh project or repo."
---

# Git Project Setup

## When to use
- User asks to create a new project/repo
- User asks to initialize something fresh
- Avoid manual repetition of .gitignore boilerplate

## Steps

```bash
new-project <dir>
```

This shell function (defined in `~/.bashrc`) does:
1. `mkdir -p "$1"`
2. `cd "$1"`
3. `git init -q`
4. Append `.env*` to `.gitignore`
5. Append `.DS_Store` to `.gitignore`
6. Print confirmation

## Verification

```bash
cd <dir>
cat .gitignore
git status
```

## For existing repos

Run this one-liner to append `.env*` if it's missing:

```bash
[ -f .gitignore ] && grep -q '^\.env\*' .gitignore || echo '.env*' >> .gitignore
```

## Global defaults already installed

- `~/.git-templates/ignore/.gitignore` contains `.env*`
- Git `init.templatedir` is set to `~/.git-templates`
- A `post-checkout` hook template auto-appends `.env*` for existing repos

## Notes

- `.env*` covers `.env`, `.env.local`, `.env.development`, etc.
- Keep `.env` for secrets only; non-secret config belongs in `config.yaml`.
