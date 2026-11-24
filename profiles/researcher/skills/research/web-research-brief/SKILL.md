---
name: web-research-brief
description: Research a topic across the open web and deliver a sourced markdown brief. Use when the user says "research X", "riset tentang X", "cari data soal X", "brief me on X", or asks for background on a region/topic — especially when they want a deliverable file plus a short chat summary. Covers source selection, extraction without a browser, cited numbers, and flagging contested claims.
---

# Web research → sourced brief

Produce a brief that a skeptical reader could check. Numbers with no attribution are worthless; a wall of prose with no file is forgettable.

## Workflow

1. **Clarify scope only if it's genuinely ambiguous.** "Research climate change in Middle East" is broad but actionable — pick the 6–9 axes that matter (scale of impact, main mechanisms, hard numbers, who's affected, economics, policy, latest developments) and go. Don't interrogate the user for a scope decision they didn't ask to make.

2. **Batch your first fetches.** In one turn, hit several independent sources in parallel. Cheap first pass:
   - Wikipedia REST summary: `https://en.wikipedia.org/api/rest_v1/page/summary/<Title>` (JSON, ~1 paragraph)
   - Wikipedia full text: `action=query&prop=extracts&explaintext=1` (dumps clean plaintext, no HTML scraping needed)
   - Wikipedia search: `action=query&list=search&srsearch=...` to find the right article title before guessing
   - Google News RSS for anything current: `https://news.google.com/rss/search?q=<terms>&hl=en-US&gl=US&ceid=US:en`
   - DuckDuckGo **lite**: `https://lite.duckduckgo.com/lite/?q=<terms>` with a normal browser UA
   - **`/llms.txt`** on any vendor docs site — flat index of every doc page, and appending `.md` to a page gives clean markdown. Beats scraping marketing pages, which are the most bot-blocked pages on the web.
   - Bing (`bing.com/search?q=...`) as the fallback when both DDG endpoints get challenged
   - Primary org pages (WMO, World Bank, IPCC, IEA, UN) — fetch the newsroom/press-release page, it carries the headline stats.

   See `references/source-access-recipes.md` for exact commands and quirks.

   If a question touches Indonesian payments, compliance, or regional infrastructure, check `references/indonesia-payments-and-compliance.md` first — it holds already-verified fee tables, UU PDP / PSE specifics, and the design-system/accessibility numbers, so you only re-verify what's changed.

3. **Prefer primary institutional sources over news for numbers.** A WMO/World Bank/IPCC page gives you the figure plus its baseline and scenario. News gives you the figure with none of that. Use news to learn *what's happening now*, then go find the institutional page that states it cleanly.

4. **Extract text with stdlib, not a browser.** Strip `<script>`/`<style>`, replace tags with newlines, unescape entities, keep only lines >60 chars. That recovers the article body from almost any CMS page in a few lines of Python. Browser tools are for interaction; this is a text-extraction job.

5. **Deliver as a file + a short chat summary.** User preference (confirmed): JSON/reports go out as **file attachments**, not pasted walls into chat. Write the markdown to `~/research/<topic>-brief.md`, then in chat give 5–8 bolded takeaways with the actual numbers, and attach the file with `MEDIA:/abs/path`.

6. **Flag contested claims explicitly.** Where the literature disagrees (e.g. drought→Syrian civil war: Kelley/Gleick pro, Selby 2017 & Ide 2018 contra), say "still debated, don't cite as consensus". This is the highest-value thing in a brief and the thing most summaries omit.

7. **Close with 3–4 research gaps** and a short source list. Gaps tell the user where the next real question is.

## Brief structure that works

The climate/impact shape below is one instance of a general rule: **order sections by how checkable they are**, and end with what you couldn't check.

**Impact/issue brief:**
1. **Why this is a hotspot / the framing** — the one-line mechanism
2. **Impacts, ordered by how concrete they are** (observed deaths/records before projections)
3. **The structural driver** (resources, economics, emissions)
4. **Paradoxes** — things that contradict the naive story (drought region gets flash floods; high emissions + world-class renewable potential)
5. **Latest 12–18 months** — current events that change the picture
6. **Research gaps**
7. **Primary sources**

**Decision/architecture brief** (tool choices, vendor comparison, "what should I learn/use"):
1. **Terms disambiguated** — if the ask spans two similarly-named things, separate them first
2. **The mental model** — the concepts that make the rest legible (auth vs capture, tokens vs components, latency vs round-trips)
3. **The hard numbers** — prices, fees, limits, thresholds, each with source + date
4. **What breaks in production** — the failure modes nobody mentions
5. **Decision matrix** — situation → choice → reason, 5–6 rows max
6. **Learning path / next actions** — weekly, each with a concrete artifact, not a reading list
7. **What I could not verify** — named, with why, and what to read instead

Both shapes end the same way and it's non-negotiable: a **"what I could not verify"** section listing each unverified claim, the reason (site blocked, headlines conflict, primary text unreachable), and where the user should look. Five or six items; more means the research isn't finished. Vague hand-waving ("data may be outdated") is worse than nothing.

Every section carries at least one number with an attribution in parentheses. If a section has no number, it's probably filler — cut it.

## Two checks that produced the highest-value lines in past briefs

**Cross-check the same number on two pages of the same source.** Vendor sites contradict themselves constantly — localized vs English page, marketing page vs docs page, headline vs table. One session: Midtrans' EN pricing page said payouts cost IDR 2,500 "to all bank accounts" while its `/id/` page said IDR 5,000 to banks / 2,500 to e-wallets. Surfacing that is a *feature* of the brief: put both numbers side by side, name both URLs, tell the user to confirm in their own dashboard. For country-specific numbers prefer the localized page and say you did.

**Disambiguate similarly-named terms in the opening section.** Users conflate adjacent fields constantly (design system vs system design, data residency vs data localization, MDR vs processing fee, latency vs round-trip count). When the request spans two such terms, spend the first section on a small table separating them and structure the whole brief along that split. Usually the most useful thing in the document, and it costs six lines.

## Pitfalls

- **`html.duckduckgo.com` returns a CAPTCHA page.** Use `lite.duckduckgo.com/lite/` — same results, no challenge. But **lite is also burst rate-limited**: 3+ queries in one loop gets the duck on every request after the first. That's a throttle, not a dead host — space the calls or switch to Bing. Never conclude "search doesn't work here".
- **Don't guess Wikipedia titles.** `page/summary/Foo` returns HTTP 404 with no hint. Run `list=search` first, or use `action=query&titles=...` which normalizes titles and tells you when a page is missing.
- **News RSS titles are enough for triage**, but never quote a stat from a headline. Open the primary source.
- **Some news sites 403 or return HTTP 202 with an empty JS shell.** Skip and find another outlet carrying the same story — don't fight the paywall/wall.
- **Wikidata/agency-year artifacts**: "hottest year on record" claims need the baseline stated (e.g. +1.08 °C *above 1991–2020 average*). Always carry the baseline alongside the number.
- **Don't fabricate to fill a section.** If a stat isn't findable, write the qualitative claim and mark it. A brief with 20 verified numbers beats 40 with 10 invented.
- **Language**: reply in the user's language (Indonesian for this user), casual register. The brief file can be Indonesian too — keep technical terms in English where that's how the field says them (water stress, attribution study).

## Output pattern

```
[brief file: ~/research/<topic>-brief.md]

## Poin inti
**1. <bolded claim>.** <numbers> (<source>)
...6–8 items max...

⚠️ <one caveat / contested claim>

MEDIA:/home/ubuntu/research/<topic>-brief.md

Mau gue dalemin ke satu sudut tertentu? <two concrete options>
```

skipped: automated source-scraping pipeline; add when the same topic needs a recurring refresh (then use a cron job, not a skill).
