# Live schema and parallel migration reconciliation

Use when a feature branch adds a migration while the deployed checkout contains newer uncommitted or unmerged schema work.

## Why clean-suite evidence is insufficient

A new database created from the feature branch can pass every test while deployment still fails because the live migration ledger and effective schema have advanced independently. Typical symptoms include:

- the feature reuses a migration number already present in production under a different filename;
- `INSERT ... SELECT *` fails after another migration added a column;
- rebuilding a constrained SQLite table drops a column introduced by parallel work;
- deploying the clean branch would replace live source/assets that contain unmerged behavior.

## Required pre-deployment gate

1. Inspect the live migration ledger by **filename**, not only count.
2. Inspect `PRAGMA table_info`, foreign keys, and indexes for every table the migration rebuilds.
3. Compare the live schema with the clean branch migration sequence.
4. Back up the actual runtime database using SQLite backup semantics.
5. Run the exact candidate binary against that backup copy on an unused port, allowing startup migrations to execute.
6. Require:
   - service-specific health response;
   - `PRAGMA integrity_check = ok`;
   - expected final migration filenames;
   - preserved row counts for affected ownership/content tables;
   - preservation of columns and indexes added by parallel work.
7. Use explicit column lists in every migration copy statement. Never use `INSERT INTO new_table SELECT * FROM old_table` when schemas may evolve independently.
8. If production already owns migration number N, rename the feature migration to N+1 and include or merge the prerequisite migration only when its exact schema is required for clean bootstrap. Do not duplicate a shipped migration under another filename.
9. Before deployment, compare feature-changed paths with dirty/untracked production paths. If they overlap, do not copy a clean feature artifact over production. Integrate the parallel work first in a clean branch/worktree, rerun all gates, then deploy.

## Status discipline

A committed and pushed feature is not deployed when the live checkout cannot safely receive it. Report the precise boundary: `implemented, verified, committed, and pushed; production deployment stopped to avoid rolling back unmerged live work.` Keep authenticated public E2E pending until the integrated artifact is actually served.
