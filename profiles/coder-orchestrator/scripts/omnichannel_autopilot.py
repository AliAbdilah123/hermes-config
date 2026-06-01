#!/usr/bin/env python3
import json
import sqlite3
import subprocess
import time
from pathlib import Path

BOARD = "omnichannel-chat-hub"
DB = Path("/home/opc/.hermes/kanban/boards/omnichannel-chat-hub/kanban.db")
MAX_SECONDS = 4 * 60 * 60
POLL_SECONDS = 60

REVIEW_MARKERS = (
    "review-required",
    "please review",
    "approve or request edits",
    "manual review",
)


def run(cmd):
    return subprocess.run(cmd, text=True, capture_output=True, timeout=180)


def comment(tid, text):
    run(["hermes", "kanban", "--board", BOARD, "comment", tid, text, "--author", "coder-orchestrator-autopilot"])


def complete_review_block(tid, title, reason):
    summary = (
        "Manual review bypassed by user. Accepting completed worker handoff "
        f"for '{title}' so downstream tasks can continue. Original blocker: {reason[:500]}"
    )
    run(["hermes", "kanban", "--board", BOARD, "complete", tid, "--summary", summary, "--result", summary])


def snapshot():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "select id,title,status,assignee,last_failure_error,result from tasks where status != 'archived' order by created_at"
    ).fetchall()
    con.close()
    return rows


def main():
    start = time.time()
    print("Autopilot started for board omnichannel-chat-hub", flush=True)
    while time.time() - start < MAX_SECONDS:
        rows = snapshot()
        active = [r for r in rows if r["status"] not in ("done", "archived")]
        if not active:
            print("All non-archived tasks are done.", flush=True)
            run(["hermes", "kanban", "--board", BOARD, "list"])
            return 0

        for r in rows:
            if r["status"] == "blocked":
                reason = (r["last_failure_error"] or r["result"] or "").lower()
                if any(m in reason for m in REVIEW_MARKERS):
                    print(f"Auto-completing review-gated task {r['id']}: {r['title']}", flush=True)
                    comment(r["id"], "Autopilot: bypassing review gate per user instruction; user will test at the end.")
                    complete_review_block(r["id"], r["title"], r["last_failure_error"] or r["result"] or "review-required")

        dispatch = run(["hermes", "kanban", "--board", BOARD, "dispatch"])
        if dispatch.stdout.strip():
            print(dispatch.stdout.strip(), flush=True)
        if dispatch.stderr.strip():
            print(dispatch.stderr.strip(), flush=True)

        # Stop early if only non-review blockers remain, so user can see the real blocker.
        rows2 = snapshot()
        blockers = [r for r in rows2 if r["status"] == "blocked"]
        real_blockers = []
        for r in blockers:
            reason = (r["last_failure_error"] or r["result"] or "").lower()
            if not any(m in reason for m in REVIEW_MARKERS):
                real_blockers.append(r)
        if real_blockers:
            print("Stopped: non-review blockers remain:", flush=True)
            for r in real_blockers:
                print(f"- {r['id']} {r['title']}: {(r['last_failure_error'] or r['result'] or '')[:500]}", flush=True)
            return 2

        time.sleep(POLL_SECONDS)

    print("Stopped: autopilot timeout reached.", flush=True)
    run(["hermes", "kanban", "--board", BOARD, "list"])
    return 3

if __name__ == "__main__":
    raise SystemExit(main())
