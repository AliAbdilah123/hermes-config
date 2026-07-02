# SQLite WAL — Recovery After Live-DB Copy or Crash

## Symptom

After copying a live SQLite database (e.g., `cp` from dev → production), the Go API repeatedly crashes at startup with:

```
database disk image is malformed (11)
```

The service enters a crash-loop. `PRAGMA integrity_check` on the source DB passes, but the copy fails.

## Root Cause

SQLite in WAL mode has three files: `app.db` (main), `app.db-wal` (write-ahead log), `app.db-shm` (shared memory index). The WAL and SHM files belong to the original process — they contain pages that haven't been checkpointed into the main DB, and their internal state references the original process's memory.

When you copy only `app.db` (or copy all three but start a different process), the WAL contents don't match the new process, and SQLite rejects the database as malformed.

## Recovery

```bash
# Stop the service first
sudo systemctl stop <service>

# Remove the WAL and SHM files — SQLite will recover from the main DB
sudo rm -f /path/to/app.db-wal /path/to/app.db-shm

# Verify the main DB is intact
sqlite3 /path/to/app.db "PRAGMA integrity_check;"
# Should output: ok

# Start the service
sudo systemctl start <service>
```

## When this works

- The main DB file (`app.db`) was checkpointed at some point and is internally consistent.
- You're willing to lose the handful of uncommitted transactions that were only in the WAL (typically seconds of data in a single-writer SQLite app).

## When this doesn't work

If `PRAGMA integrity_check` fails after removing WAL/SHM, the main DB file itself is corrupt. You need a backup. Prevent this by:

- Copying DB files while the service is stopped (safe but downtime).
- Using `sqlite3 app.db "VACUUM INTO '/tmp/backup.db'"` or `.backup` from a live connection (safe, no downtime).
- Running the Go service with a startup checkpoint: `PRAGMA wal_checkpoint(TRUNCATE)` before graceful shutdown.

## Prevention for deploy scripts

When deploying a SQLite-backed Go binary, don't `cp` the raw DB files while the service is running. Instead:

```bash
# Safe copy via sqlite3 (works while source DB is open)
sudo systemctl stop <service>         # stop target
sqlite3 /source/app.db ".backup /target/app.db"   # live backup from source
sudo systemctl start <service>        # start target
```
