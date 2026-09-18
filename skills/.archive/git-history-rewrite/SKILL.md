---
name: git-history-rewrite
description: "Git history rewrite workflows: drop large/unwanted files from all commits, force-push cleanup, and verify the result safely."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, rewrite, history, cleanup, large-files, filter-repo, bfg, filter-branch]
    related_skills: [systematic-debugging]
---

# Git History Rewrite

## Purpose

Permanently remove files from git history so local path deletions aren't enough:
- Large untracked/cache files that now exceed remote limits
- Secrets committed in history
- Vendor directories/compiled assets/tool caches checked in by accident

## Preferred Order

1. **git filter-repo** (fastest, maintained)
2. **BFG Repo-Cleaner** (simpler for mass deletes)
3. **git filter-branch** (last resort, slower, more failure modes)

## Workflow

### 1. Inspect current state
- Clone or create a clean scratch working copy
- Count offending files/paths already tracked
- Confirm tooling availability (`which git-filter-repo`, `which java`)
- Check whether repository has tags, shallow clones, or partial clone configs that could break rewrites

### 2. Add a .gitignore rule FIRST
Add the path pattern to `.gitignore` in the target repo before rewriting so the cleanup sticks.

### 3. Rewrite with the strongest available tool
#### With git filter-repo
```bash
git filter-repo --invert-paths -p /path/to/dir
```
- `-p` avoids rewrite failures from missing path permutations
- Use globs when needed, e.g. `**/pnpm/store/**`

#### With BFG Repo-Cleaner
```bash
bfg --delete-files bigfile.bin
bfg --delete-folders .pnpm
```
- Much faster than filter-branch for single large files/dirs

#### With git filter-branch (last resort)
```bash
git filter-branch -f \
  --index-filter 'git rm -r --cached --quiet --ignore-unmatch target-path' \
  --prune-empty --tag-name-filter cat -- --all
```
- Used only if the above tools are unavailable
- Read any emitted warnings carefully
- Do NOT kill it early; kill cancels the rewrite and leaves partial state

### 4. Just-in-time safety checks
- When rewriting large repos, set safe shell flags and write a small cached helper if recursion is used, but prefer the existing tools over manual recursion
- Confirm phrase before rewriting: e.g., the intended path prefix must match exactly
- If a partial/globbing rewrite is needed, use the platform-accepted form (`profiles/*/home/.local/share/pnpm/**`) consistently across checks and filters
- When merges exist and the failure mode involved rewriting non-HEAD refs, switch from single-tree helpers to a full ref traversal that references untouched parents directly; this avoids duplicating the full unchanged subtree on every merge commit and reduces memory churn on large repos
- If memory pressure occurs on big repos, complete the full-ref pass, retry once with smaller batch commands, then stop and hand back control instead of rerunning identical heavy loops
- Some bulk removals still produce post-rewrite warnings like “non-existent ancestor.” These are general housekeeping notes; when the rewritten tree truly had no matching files, they usually do not indicate a regression, but do verify by scanning the rewritten tree before pushing

### 5. Finalize
- Expire and prune reflog/refs
- Run garbage collection
- Verify no tracked files remain at the offending path
- Force-push when the remote rejects large files

## Safety
- Require explicit confirmation before force-pushing
- Do not interleave half-applied rewrites with status inspection
- If a rewrite attempt gets interrupted, start fresh from a clean working copy rather than resuming from partial state

## Scripts

Use `scripts/rewrite-drop-pnpm.sh <repo-path> [glob-pattern]` for the recurring pnpm cache cleanup case.