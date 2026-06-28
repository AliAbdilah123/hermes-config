---
name: scraped-business-data-product-analysis
description: Analyze scraped local-business datasets and turn them into product/PRD recommendations, lead intelligence, enrichment, automation, and AI feature roadmaps.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [scraping, local-business, csv, lead-scoring, product-analysis, prd, crm, automation]
    category: data-science
---

# Scraped Business Data Product Analysis

Use this skill when the user provides scraped business/location/directory data (CSV, spreadsheet, JSON, web export) and asks what they can do with it, how to analyze it, or how an app can enhance it with analysis, calculations, automation, cron jobs, AI integration, CRM, or outreach features.

## Outcome

Deliver both:

1. **Grounded dataset analysis** based on the actual file contents.
2. **Actionable product direction**: app concept, features, scoring models, workflows, automations, and roadmap.

For this user, when the request is product/application ideation or a review document, also create a **styled HTML review/PRD artifact** under the relevant project path at `docs/<name>.html`, publish it under `/prd/<name>.html` when possible, and verify the public/cache-busted URL contains specific expected text before finalizing.

## Workflow

1. **Inspect the data first**
   - Read headers, row count, sample rows, file size.
   - Identify column types: name/title, rating, review count, address, phone, website/social link, coordinates, category, session/query, scrape date.
   - Do not infer metrics from memory; compute them from the uploaded file.

2. **Profile quality and coverage**
   - Missing values by important column.
   - Contactability: phone/email/WhatsApp coverage.
   - Digital presence: website vs social-only vs blank.
   - Location/geography coverage.
   - Duplicate risk by exact/near name, phone, website, coordinates, or address.
   - Distribution metrics: average/median rating, total/median/max reviews, category keyword counts.

3. **Find monetizable segments**
   - High rating + high reviews + no website.
   - Social-only businesses that need landing pages/conversion funnels.
   - Low-review but high-rating businesses that need review generation.
   - High-review incumbents for competitive benchmarks.
   - Category/location clusters where sales territories or campaigns can be targeted.

4. **Create a transparent score model**
   - Example for lead generation:
     - Missing website: +30 if blank, +15 if social-only.
     - Rating quality: +25 if rating ≥4.7, +10 if ≥4.3.
     - Review volume: +25 if ≥40, +15 if ≥10, +5 if lower.
     - Contactability: +20 if phone/WhatsApp exists.
     - Category fit: +5 to +10 for target keywords.
     - Duplicate risk: subtract for duplicate coordinates/phone/name clusters.
   - Use Bayesian ranking for “best businesses” so a 5.0 rating with 1 review does not outrank a 5.0 rating with hundreds of reviews.

5. **Translate analysis into app features**
   - CSV/import pipeline: normalization, validation, dedupe, enrichment queue.
   - Lead dashboard: filters, segments, saved views, maps, charts.
   - CRM/kanban: New → Qualified → Contacted → Replied → Meeting → Won/Lost.
   - AI enrichment: classify business type, summarize weaknesses, infer offer angle, generate tags.
   - Pitch generator: WhatsApp/email scripts tailored by segment.
   - Website/SEO auditor: website presence, SSL, mobile, CTA, meta tags, broken links, screenshots.
   - Cron monitoring: scheduled re-scrapes/imports, review/rating deltas, new competitor alerts, weekly market reports.
   - ROI calculators: expected leads, conversion rate, average project/order value, ad spend, payback.

6. **Produce deliverables**
   - Concise chat summary with the highest-value findings and recommended app direction.
   - If requested or useful for review: styled HTML PRD/review artifact with metrics, tables, scoring formula, feature roadmap, and tech direction.
   - End with the public project/PRD link when a public artifact is created.

## HTML PRD structure

Recommended sections:

- Hero: dataset, vertical, geography, thesis.
- Metric cards: rows, phone coverage, website coverage, average rating, total reviews.
- “What you can do with this data”.
- Observed segments and geographic concentration.
- Highest-priority leads table.
- Product feature roadmap: MVP, V1, V2.
- Scoring formula.
- Tech direction including frontend with `shadcn/ui` when relevant.
- Automation/cron and AI integration sections.

## Publishing and verification

- Store artifact in the relevant project under `docs/<slug>.html`.
- Publish under the configured public PRD route, typically `/prd/<slug>.html`.
- If `/prd/` maps to `/usr/share/nginx/html/prds/`, copying the file may work better than symlinking when nginx cannot traverse the project path.
- Verify with `curl` that the public cache-busted URL returns HTTP 200 and contains at least 2-3 unique strings from the new artifact.

## Pitfalls

- Do not stop at generic suggestions; compute actual metrics from the file and name real segments/leads.
- Do not over-trust raw star ratings; include review volume and Bayesian scoring.
- Do not treat missing website as bad data only; it can be the main commercial opportunity.
- Do not publish a stale/cached URL without verifying the new text is visible.
- Avoid one-off hardcoding in the product concept; frame the app as reusable across verticals/cities/categories.

## References

- `references/interior-scrape-example.md` — concrete example from an interior-design Balikpapan scrape, including metrics and feature mapping.
