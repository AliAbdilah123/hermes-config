# Implementation checklist

Persist provider settings per workspace; validate absolute HTTP(S) URL and absolute workspace paths; public DTO returns `has_secret`, never token. Claim jobs with conditional SQL and lane serialization. Persist provider session ID immediately. Feedback/implementation resumes that session. Reconcile interrupted sessions at startup and after restarts. Fork creation creates branch/worktree plus DB row with compensation on either failure. Merge preview records source HEAD; confirmation re-reads HEAD and rejects mismatch. Bound SQLite busy retries and record each lifecycle transition as an event.

Tests: concurrent scheduler, terminal lane release, session reuse, missing-session reconciliation, runtime symlink/path escape, partial fork cleanup, merge watermark, stale review approval, busy retry ceiling.
