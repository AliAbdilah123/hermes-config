# PRD implementation gap review

Use when the user asks which parts of a PRD/spec are not implemented in an app.

## Workflow

1. Fetch/read the PRD and extract the feature groups, acceptance checks, endpoints, tables, and UI promises.
2. Locate the project from channel context, memory, URL hints, or current working directory. If uncertain, search likely project roots before asking.
3. Compare the PRD against concrete implementation evidence, not screenshots or guesswork:
   - backend routes/handlers for promised endpoints
   - DB migrations/table creation and added columns
   - frontend nav/pages/components/buttons/modals
   - tests for acceptance criteria
   - deployed build only if the question asks about live behavior
4. Search by durable nouns from the PRD: table names, endpoint suffixes, component labels, and feature terms. Examples: `enrichment_runs`, `website_audits`, `lead_activities`, `outreach_campaigns`, `scheduled_jobs`, `/api/v1/segments`, `website-audit`.
5. Classify each PRD group as one of: implemented, mostly implemented, partially implemented, mostly missing, not implemented.
6. Answer with a concise gap list. Include evidence paths or names when useful, and separate “basic/adjacent existing feature” from the actual PRD requirement.

## Pitfalls

- Do not count an adjacent feature as implemented. Example: a website generator/draft feature is not the same as a Website/SEO Audit with `website_audits` storage and audit endpoints.
- Do not count placeholder/Soon UI as implementation.
- Do not claim a feature is missing solely because the frontend lacks it; check backend tables/routes too.
- Avoid full PRD re-summarization unless asked. The user usually wants the missing points.
