#!/usr/bin/env python3
"""Resolve what a router alias/combo actually serves, and show recent routing history.

Usage:
    resolve_combo.py <alias> [base_url] [--key KEY] [--db PATH]

Defaults: base_url=http://127.0.0.1:20128, key read from ~/.hermes/.env OPENAI_API_KEY,
db=~/.9router/db/data.sqlite (skipped if absent).

Why this exists: a gateway alias is not a model. The only authoritative answer is the
`model` field the router writes into the response, plus its usage history. One runnable
check instead of hand-typing curl one-liners (which trip the agent's command parser).
"""
import argparse
import json
import os
import sqlite3
import sys
import urllib.request


def read_key(explicit):
    if explicit:
        return explicit
    env = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env):
        for line in open(env):
            if line.startswith("OPENAI_API_KEY="):
                return line.split("=", 1)[1].strip()
    return os.environ.get("OPENAI_API_KEY", "")


def probe(alias, base_url, key):
    """Send a tiny request for `alias`; the router rewrites `model` to the real upstream."""
    body = json.dumps({
        "model": alias,
        "messages": [{"role": "user", "content": "reply with just the word ping"}],
        "max_tokens": 5,
    }).encode()
    req = urllib.request.Request(
        base_url.rstrip("/") + "/v1/chat/completions",
        data=body,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    )
    raw = urllib.request.urlopen(req, timeout=60).read().decode()
    # Routers may answer text/event-stream even for non-stream requests -> not plain JSON.
    for chunk in raw.split("data: "):
        chunk = chunk.strip()
        if not chunk or chunk == "[DONE]":
            continue
        try:
            return json.loads(chunk)
        except json.JSONDecodeError:
            continue
    raise RuntimeError("no JSON payload in response: " + raw[:200])


def probe_models(base_url, key):
    req = urllib.request.Request(
        base_url.rstrip("/") + "/v1/models",
        headers={"Authorization": "Bearer " + key},
    )
    return [m.get("id") for m in json.load(urllib.request.urlopen(req, timeout=20)).get("data", [])]


def combos(db):
    if not os.path.exists(db):
        return []
    con = sqlite3.connect(db)
    try:
        return con.execute("select name, models from combos").fetchall()
    except sqlite3.Error:
        return []
    finally:
        con.close()


def history(db, alias, limit=10):
    if not os.path.exists(db):
        return []
    con = sqlite3.connect(db)
    try:
        rows = con.execute(
            "select timestamp, provider, model, cost from usageHistory"
            " order by timestamp desc limit ?", (limit,)).fetchall()
    except sqlite3.Error:
        return []
    finally:
        con.close()
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("alias")
    ap.add_argument("base_url", nargs="?", default="http://127.0.0.1:20128")
    ap.add_argument("--key")
    ap.add_argument("--db", default=os.path.expanduser("~/.9router/db/data.sqlite"))
    a = ap.parse_args()

    if not os.path.exists(a.db):
        a.db = os.path.expanduser("~/.hermes/db/data.sqlite")
    key = read_key(a.key)
    fail = 0

    print("alias:       ", a.alias)
    print("gateway:     ", a.base_url)

    c = dict(combos(a.db))
    known = c.get(a.alias)
    if known:
        print("combo members:", known)
    elif c:
        print("combos known: ", list(c.keys()))

    try:
        r = probe(a.alias, a.base_url, key)
        print("SERVED BY:   ", r.get("model"), "(response id", r.get("id"), ")")
        print("content:     ", (r.get("choices") or [{}])[0].get("message", {}).get("content"))
    except Exception as e:  # noqa: BLE001
        fail = 1
        print("PROBE FAILED:", type(e).__name__, e)

    try:
        ids = probe_models(a.base_url, key)
        hits = [i for i in ids if a.alias in i]
        print("models list:  %d entries" % len(ids), "| alias matches:", hits)
    except Exception as e:  # noqa: BLE001
        print("models list:  unavailable (%s)" % type(e).__name__)

    h = history(a.db, a.alias)
    if h:
        print("\nrecent routing history (timestamp | provider | model | cost):")
        for row in h:
            print("  ", " | ".join(str(x) for x in row))

    if fail:
        print("\nhint: APIConnectionError on one client while 127.0.0.1 works => the client's"
              " base_url uses 'localhost' and resolves to ::1. Point it at 127.0.0.1.")
    return fail


if __name__ == "__main__":
    sys.exit(main())
