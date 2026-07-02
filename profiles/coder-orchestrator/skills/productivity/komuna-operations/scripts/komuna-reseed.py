#!/usr/bin/env python3
"""Complete Komuna reseed: auth_users + app_state with all programs, products, members, etc.

This script was used to reseed 40 users, 25 programs (5 East Kalimantan fitness + 20 global),
10 products, 64 memberships, and associated sessions/packages/vouchers/claims.

Usage:
    sudo systemctl stop komuna-api.service
    python3 komuna-reseed.py
    sudo systemctl start komuna-api.service

IMPORTANT: This DESTROYS the existing database. Use only when the user explicitly
asks for a full reseed from scratch.
"""
import hashlib, secrets, sqlite3, json, os
from datetime import datetime, timezone, timedelta

DB = '/home/ubuntu/projects/komuna/sqlite.db'
DEFAULT_PW = 'komuna123'
now_str = lambda: datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
t = datetime.now(timezone.utc)
ts = lambda h_offset=0: (t + timedelta(hours=h_offset)).strftime('%Y-%m-%dT%H:%M:%SZ')

def hash_password(password):
    salt = secrets.token_hex(16)
    buf = (salt + ":" + password).encode()
    for _ in range(120000):
        buf = hashlib.sha256(buf).digest()
    return f"{salt}:{buf.hex()}"

# See full script at /tmp/komuna-reseed.py for the complete data
# Key patterns demonstrated:
# - Programs: use Go field names as JSON keys (TitleCase)
# - Products: 2 per Kaltim program, each with session products
# - Members: roles use lowercase JSON tags ("role", "product_id")
# - Packages: ValidityValue is *int in Go — use integer, NOT string
# - State MUST include all keys: Programs, Products, Packages, Sessions,
#   Members, Vouchers, Claims, Requests, Purchases, Audit, Notifications, Settings
