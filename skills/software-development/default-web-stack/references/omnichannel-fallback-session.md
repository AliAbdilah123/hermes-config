Omnichannel hub build session.

Key decisions
- Chose React + TS frontend + Flask backend + SQLite as fallback when Go toolchain was unavailable in the environment.
- Kept TS/React frontend intact; switched backend only, preserving user preference against arbitrary stack substitutions.

Current API surface
- GET /api/v1/health
- GET /api/v1/channels
- POST /api/v1/channels
- POST /api/v1/channels/{id}/connect
- POST /api/v1/channels/{id}/disconnect
- GET /api/v1/channels/{id}/logs
- GET /api/v1/conversations
- POST /api/v1/conversations
- GET /api/v1/conversations/{id}/messages
- POST /api/v1/conversations/{id}/messages
- GET /api/v1/stats
- POST /api/v1/ingest HMAC webhook handler

Verified setup
- /home/opc/omnichannel-hub/db/schema.sql matches backend table usage
- /home/opc/omnichannel-hub/backend/app.py Flask service with SQLite WAL + per-request ensure_db()
- Frontend scaffold under /home/opc/omnichannel-hub/frontend with Vite React TS template

Patch targets for next session
- Ensure tsconfig.json includes src only; remove duplicate stack rule block from SKILL.md.
- Add fallback-stack rule: if go is missing, build python3 -m venv .venv, pip install flask/flask-cors, then proceed.
