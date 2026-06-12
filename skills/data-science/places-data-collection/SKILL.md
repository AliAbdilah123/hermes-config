---
name: places-data-collection
title: Places Data Collection
description: Collect Points-of-Interest (cafes, restaurants, venues) for a target city and compile into a verifiable SQLite artifact when Google Maps UI is unavailable.
---

# Places Data Collection

Collect Points-of-Interest (cafes, restaurants, venues) for a target city and compile into a verifiable SQLite artifact.

## Trigger

- User asks for "all cafes/restaurants/places in <city>" with output to SQLite/CSV
- Primary source (Google Maps browser UI) is unavailable, rate-limited, or timing out
- User wants real lat/lng + contact fields, not scraped lists

## Procedure

### 1. Establish the database first

```python
sqlite3.connect('/path/to/output.sqlite')
cur.execute('''
CREATE TABLE IF NOT EXISTS places (
    id INTEGER PRIMARY KEY,
    name TEXT,
    address TEXT,
    lat REAL,
    lng REAL,
    phone_number TEXT,
    website TEXT,
    whatsapp_number TEXT,
    category TEXT
)
''')
```

Deliverable must be a real file on disk with runnable insert results, not a stub.

### 2. Collect venue names + coordinates via OSM Nominatim

Google Maps browser UI is unreliable in headless/orchestrated sessions (repeated 60s timeouts). Default to OSM Nominatim for structured POI data with lat/lng.

- Endpoint: `https://nominatim.openstreetmap.org/search`
- Params: `format=json&q=<query>&limit=100&addressdetails=0&accept-language=en`
- Rate limit: >= 1.1s between requests (OSM usage policy)
- Query strategy: use varied local-language and English queries per category:
  - cafes: `cafe in <city>`, `kedai kopi di <city>`, `coffee shop <city>`, `warnet kopi <city>`
  - restaurants: `restaurant in <city>`, `restoran di <city>`, `warung makan <city>`, `rumah makan <city>`, plus cuisine-specific terms (`seafood`, `padang`, `sate`, `pizza`, etc.)
- Filter results strictly to target city using address string inclusion.
- Dedup by `place_id` or `osm_id`.

### 3. Enrich contact fields (optional, noisy)

Phone/website/whatsapp are not reliably in OSM. To enrich:
- Search DuckDuckGo HTML (`https://html.duckduckgo.com/html/?q=...`) for `<name> <city> telepon website`
- Parse result titles/URLs/snippets
- Validate matched numbers with at least 8 digits and country-aware formatting
- **Do not fabricate contact data** — leave NULL if unverified.

### 4. Export and verify

```python
# Final commit + spot check
cur.execute('SELECT COUNT(*) FROM places')
cur.execute('SELECT name, lat, lng FROM places LIMIT 5')
```

Report:
- Total rows collected
- Coverage: how many have lat/lng vs contact fields populated
- Any gaps or rate-limit interruptions

## Pitfalls

- **Google Maps browser = dead end** in this environment. Do not retry it as the primary path after two consecutive timeouts.
- **OSM coverage gaps**: small/chain venues may be missing. List what was searched, not just what was found.
- **Enrichment noise**: regex phone scrapes often match unrelated digits (street numbers, lat/lng fragments). Filter by length and country context; prefer leaving NULL over bad data.
- **Rate limits**: stay at 1 req/s for Nominatim; longer backoff if 429/HTTP errors appear.
- **Schema mismatch**: deliver the exact columns requested (`id, name, address, lat, lng, phone_number, website, whatsapp_number`). Do not rename.

## Support Files

- `references/query-bank-<city>.md`: pre-vetted query strings per category and language for a specific city (useful when OSM results skew to generic terms).
