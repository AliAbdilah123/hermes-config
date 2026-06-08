# Consumer/community UX redesign checklist

Use this when a deployed app technically works but the user says it feels too corporate, dashboard-like, or data-first.

## Product direction

Shift the default experience from **data-first** to **people/action-first**:
- Make the first screen answer: "What can I do now, who can I connect with, and what is happening near me?"
- Put analytics, audit trails, settings, and operator controls behind clearly secondary organizer/admin labels.
- Rename corporate sections into human terms: Dashboard → Today/Home, Programs → Circles, Sessions → Events, Wallet → My passes, Analytics → Organizer view, Audit → Safety log.
- Prefer warm empty states and microcopy over platform/spec language.

## UI patterns that worked

- Warm hero with a direct user question, e.g. "What do you want to do with your community today?"
- Personal/member card instead of status/health metric box.
- Quick actions with verbs and icons: Book, Join, Share, Welcome.
- "Community pulse" feed for notifications/updates.
- "Suggested for you" event/session card instead of a table/list.
- Replace raw stat boxes with story cards: "3 passes ready", "3 circles to explore", "3 upcoming sessions" plus a short human explanation.
- Keep existing data and mutations intact; this is often a frontend language/layout pass, not an API rewrite.

## Verification

After building and deploying, verify both behavior and tone:
- `npm run build` / project build command passes.
- Static deploy and project-prefixed API routes still return 200/valid JSON.
- Headless DOM smoke checks assert the new human-facing phrases are present.
- Capture a screenshot for visual review; compare against the original complaint, not just against pixel correctness.

## Pitfalls

- Do not merely recolor a dashboard; reduce the primacy of metrics and admin words.
- Do not remove admin features if they are part of the product; demote them behind organizer/admin navigation.
- Avoid replacing the stack or backend when the complaint is about product feel.
- Avoid large API changes for a UX-tone complaint unless the UI truly lacks required data.
