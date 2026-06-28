# Interior Scrape Example — Balikpapan Local Business Dataset

Use this as a compact reference for future scraped-business-data analysis sessions.

## Input shape

CSV columns observed:

- `Session ID`
- `Title`
- `Rating Score`
- `Review Count`
- `Address`
- `Phone`
- `Website`
- `Coordinates`

Dataset represented Google/local-directory style scrape results for “desain interior balikpapan”.

## Computed metrics from the session

- Rows: 61 businesses
- Phone coverage: 93.4% — 57/61 had phone numbers
- Website coverage: 49.2% — 30/61 had websites, 31 had no website
- Average rating: 4.86
- Rating range: 3.6 to 5.0
- Total reviews captured: 1,678
- Median reviews: 5
- Max reviews: 397
- Duplicate coordinate groups: 12

Keyword/category counts:

- Interior-related: 43
- Architecture/build/renovation-related: 11
- IKN/regional expansion keywords: 5
- Digital/social presence keywords: 10
- Office/commercial keywords: 4

Subdistrict concentration:

- Balikpapan Selatan: 23
- Balikpapan Utara: 20
- Balikpapan Kota: 9
- Balikpapan Tengah: 3
- Balikpapan Tim.: 1

## High-priority no-website leads found

These were strong examples of “high proof + weak digital presence”:

| Business | Rating | Reviews | Why high priority |
|---|---:|---:|---|
| PT YASKA ANUGERAH PERSADA | 5.0 | 163 | Strong review proof, no website captured |
| Kolomarsi / PT.HBS | 5.0 | 54 | Architecture/build/interior keywords, no website captured |
| Jasa Interior Di Balikpapan | 4.9 | 56 | Exact-match local keyword name, no website captured |
| KIPALOP furniture and interior custom Balikpapan | 4.9 | 56 | Custom furniture positioning, no website captured |
| INTERIOR BALIKPAPAN 129 | 4.9 | 56 | Category exact-match name, no website captured |
| GRAHA PIRAMIDA GROUP | 4.8 | 44 | Enough review volume for trust, no website captured |

## Product concept that worked

Position the app as **Local Business Growth Radar**:

- Converts scraped local-business data into prioritized prospects.
- Adds CRM, enrichment, outreach, monitoring, and reports.
- Best initial customer: agencies/consultants selling websites, landing pages, local SEO, WhatsApp automation, ads, or review generation to SMBs.

## Feature mapping

The user specifically asked for possible features around analysis, calculation, automation, cron jobs, and AI integration. The useful mapping was:

- Analysis: coverage, dedupe, market segments, geographic concentration, competitor benchmarks.
- Calculation: lead score, Bayesian rating score, ROI calculator, review-growth deltas.
- Automation: import pipeline, CRM task creation, follow-up reminders, bulk export/WhatsApp links.
- Cron jobs: nightly/weekly re-scrape, rating/review change alerts, new competitor alerts, weekly reports.
- AI: business classification, weakness summary, personalized WhatsApp/email pitch, reply analysis, objection handling, website audit explanation.

## Publishing lesson

When publishing the styled HTML PRD:

- The project artifact was stored at `docs/scrape-interior-analysis-prd.html`.
- The public route `/prd/` mapped to `/usr/share/nginx/html/prds/` in nginx.
- Symlinking from `/usr/share/nginx/html/prds/` to the project file returned 403 because nginx could not traverse/read the target path.
- Copying the file into `/usr/share/nginx/html/prds/` and setting mode 644 returned HTTP 200.
- Always verify public output with a cache-busted URL and unique strings from the artifact.
