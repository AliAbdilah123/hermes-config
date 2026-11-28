# Re-evaluating a plan against current code

Companion to the "Re-evaluating a plan against current code" section in SKILL.md.
Captured from the Growing Guild session where "reevaluate based on the current
state of code" was asked after the original plan's phases had already shipped.

## Why this matters

A plan written earlier often gets fully implemented, then more features get
requested and added as amendments (A–H) to the same canonical markdown. When the
user asks to "reevaluate," the plan file is a mix of already-shipped phases and
not-started amendments. Re-reading the plan cannot tell them apart — only the
live schema, routes, and types can.

## Ground-truth sequence

```bash
git status --short          # is the tree clean?
git branch --show-current
git log -8 --oneline        # did a commit already close the original plan?
```

Then read the three sources of truth in this order:

1. `server/db.go` — the `schema` var + `ensureColumn`/migration backfills. Every
   table/column named here is shipped; anything absent is not started.
2. `server/http.go` — the `mux.HandleFunc(...)` table. This is the complete,
   unambiguous API surface. `grep` it for the feature's route stem.
3. `web/src/lib/types.ts` — the binding TS contract. Enums/interfaces here mirror
   what the backend actually returns.

Evidence token per feature = table/column name, route path, or type union member.

## What "not started" actually looks like

For each amendment feature, search for its tokens and confirm absence:

| Feature | Missing-token evidence |
|---|---|
| Events | no `events` / `post_events` table, no `/events` route |
| Membership periods / rejoin | `group_members` still the composite-key table; no `group_memberships` history |
| Monthly debt / settlement | charges keyed only by `period_key`; no `service_month`, `settlements`, discounts |
| Custom member fields | no field-definition or field-value tables |
| Member self-payment | only admin `POST /charges/{id}/payments`; no checkout/proof/approval/webhook |
| Multi-level badge visibility | `badges.visibility` still `visible|hidden` (binary) |
| Public post visibility | no `visibility` on posts; only notes have a public token route |
| Schedule/grace/reminders | no billing-policy or reminder tables, no scheduler |

## The corrections section is the real deliverable

The status table proves *what* is done. The corrections section proves the plan
was *re-read against reality*, and is what prevents a greenfield rewrite of a
live model. Write each correction as: "the plan framed X as new, but Y already
exists, so X is a migration that must preserve Z."

Example from the session:

> Billing is `paid_days` entitlement, not service months. The shipped model
> derives a single entitlement expiry from `paid_days`; charges are identified
> by `period_key`. Feature C's `service_month` + settlements is a migration of
> an already-live model, not greenfield — it must add columns additively and
> backfill `period_key` charges while keeping entitlements valid.

Also state explicitly that no product/migration/deploy code was written for the
not-started items — they remain plan-only until explicit approval.

## Publishing the updated artifact

The review HTML is generated from the canonical markdown with Python `markdown`
(no `pandoc` on this host). To add a new section to an already-published HTML
without full regeneration:

1. In the markdown, append the section after the final `---` (use a heredoc with
   a unique delimiter; `patch` on a bare `---` matches many lines).
2. `markdown.markdown(section, extensions=['tables','fenced_code','sane_lists'])`.
3. Insert the fragment before `</article></main>` and add a TOC link before
   `</nav>` so the heading is reachable.
4. `chmod 644` + `sudo ln -sfn` into `/usr/share/nginx/html/prds/`, then verify
   with a fresh `?v=` cache-buster: HTTP 200 **and** `grep -c '<heading>' > 0`.

## Recommended delivery order when a plan was already partly shipped

Lead with shipped-but-done (mark "no further work"), then the net-new items in
dependency order. Dependency rule: the history/identity table first
(`group_memberships`), then the billing model that depends on it, then features
that reference the membership id, then surface/UX features, then anything needing
a scheduler or external provider last.
