# Implementation details

Importer: explicit aliases -> normalized row -> duplicate index -> transaction batch -> immutable row outcome. Enrichment rules have stable IDs and result evidence. Conversion inserts prospect and opportunity in one idempotent transaction. Transition update uses `WHERE id=? AND version=? AND stage=?`, then appends history. Files use temp+atomic rename and compensation. Outreach persists attempt before dispatch; ambiguous retry reuses its key.
