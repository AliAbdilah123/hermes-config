# Realtime, files, notifications

SSE authorizes workspace+conversation at subscribe and every event; reconnect cursor replays durable events. Cursor history uses `(created_at,id)` ordering. Files stage under generated confined paths, sniff bytes, finalize attachment transactionally, and cleanup expired stages. Notification policy checks membership, mute/DND and active presence before durable outbox insertion; sends happen outside DB transactions with backoff.
