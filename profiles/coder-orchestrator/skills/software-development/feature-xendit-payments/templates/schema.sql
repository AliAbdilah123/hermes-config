PRAGMA foreign_keys = ON;

CREATE TABLE purchases (
  id TEXT PRIMARY KEY,
  buyer_id TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','paid','failed','cancelled','expired','refunded')),
  currency TEXT NOT NULL,
  amount INTEGER NOT NULL CHECK (amount > 0),
  client_idempotency_key TEXT NOT NULL,
  intent_hash TEXT NOT NULL,
  xendit_invoice_id TEXT,
  invoice_url TEXT,
  invoice_expires_at TEXT,
  invoice_creation_status TEXT NOT NULL DEFAULT 'creating' CHECK (invoice_creation_status IN ('creating','created','invoice_creation_failed')),
  retry_count INTEGER NOT NULL DEFAULT 0,
  next_retry_at TEXT,
  paid_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE (buyer_id, client_idempotency_key),
  UNIQUE (xendit_invoice_id)
);

CREATE TABLE purchase_entry_snapshots (
  id TEXT PRIMARY KEY,
  purchase_id TEXT NOT NULL REFERENCES purchases(id) ON DELETE CASCADE,
  source_entry_id TEXT NOT NULL,
  benefit_type TEXT NOT NULL,
  product_id TEXT NOT NULL,
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  validity_days INTEGER,
  snapshot_json TEXT NOT NULL
);

CREATE TABLE payment_finalizations (
  purchase_id TEXT PRIMARY KEY REFERENCES purchases(id),
  provider_invoice_id TEXT NOT NULL UNIQUE,
  provider_status TEXT NOT NULL,
  amount INTEGER NOT NULL,
  currency TEXT NOT NULL,
  finalized_at TEXT NOT NULL
);

-- Entitlement tables should carry purchase_id and enforce their own natural uniqueness.
