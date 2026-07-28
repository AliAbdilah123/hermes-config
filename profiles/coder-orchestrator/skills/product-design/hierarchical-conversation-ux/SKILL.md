---
name: hierarchical-conversation-ux
description: Plan and prototype task/job conversations with parent-child forks, semantic merges, progress visibility, and multi-agent-ready state separation across cards, detail modals, and dedicated conversation views.
version: 1.0.0
metadata:
  hermes:
    tags: [ux, conversations, branching, jobs, progress, prototypes]
---

# Hierarchical Conversation UX

Use when designing or refining products where a task/job has a main conversation, users can fork focused discussions, and important conclusions later merge into a parent conversation. Also use when showing branch/subagent progress on compact and expanded work surfaces.

## Core model

Keep four dimensions distinct:

1. **Parent work status** — todo, running, blocked, done.
2. **Conversation topology** — main conversation, parent/child forks, fork points, merge history.
3. **Conversation progress** — active, waiting, ready to merge, merged/resolved.
4. **Actor activity** — user, agent, or future subagent working inside a conversation.

Never derive parent job status from fork status unless the product explicitly defines that policy. Conversation progress is secondary metadata.

## Workflow

1. Inspect the current job card, detail modal, timeline, routes, responsive behavior, and visual tokens.
2. Record confirmed interaction decisions separately from still-open presentation choices.
3. Model the topology and mutations: create sibling forks, navigate descendants, merge to direct parent, and reactivate after later activity.
4. Design progressive disclosure across the job card, detail modal, and dedicated conversation page.
5. Provide alternatives only for undecided dimensions. Do not re-open already-confirmed UX choices.
6. Produce a focused prototype using the product’s real shell and tokens.
7. Make primary review interactions exercisable where practical.
8. Verify exact requested labels, interaction hooks, responsive behavior, and the public artifact after the final edit.

## Progressive surface hierarchy

Use progressively richer representations rather than duplicating a full tree everywhere:

- **Job card:** aggregate only; preserve scanning and keep job status primary.
- **Job detail modal:** aggregate plus a few actionable forks and a link to full detail.
- **Dedicated conversation page:** complete tree, active transcript, fork creation, merge review, and activity state.

Hide fork progress when no forks exist; avoid decorative `0 forks` UI.

## Dedicated conversation view

For branch-heavy work, prefer an editor-style split view:

- collapsible parent/child tree on the left;
- one focused conversation on the right;
- breadcrumb for the active branch;
- direct-parent merge only when the active conversation is a fork;
- mobile tree rendered as a sheet or picker rather than a squeezed column.

Keep the existing job modal compact. When deep discussion would overcrowd it, add a native new-tab link to the dedicated conversation route.

## Fork creation

Support contextual and terminal fork points:

- a message menu forks from that event;
- a footer action forks from the latest event in the active conversation.

For parallel exploration, one dialog may accept multiple opening replies. Each non-empty field creates a sibling fork from the same parent and fork point. Create all siblings transactionally. Generate concise labels from opening replies in V1 rather than adding branch-title fields without demonstrated need.

## Semantic merge

Merge reviewed conclusions, not raw transcripts:

1. Generate important points from child activity since its previous merge watermark.
2. Let the user edit, add, remove, and reorder points.
3. Append one immutable merge card/event to the direct parent.
4. Keep the child readable for audit and context.
5. Mark it unmerged again when later child activity occurs.
6. Make confirmation idempotent and detect stale previews.

Nested branches merge one level upward unless choosing another target is an explicit product feature.

## Progress alternatives

Show each alternative on both the card and modal:

### Compact aggregate

- Card: `N forks · M active` plus attention only when needed.
- Modal: one count strip.
- Lowest density; weakest branch identity.

### Segmented aggregate

- Card: resolved/total with a thin segmented indicator.
- Modal: same aggregate plus at most three actionable rows.
- Usually the strongest default: scanable without becoming a mini tree.

### Named chips or rows

- Card: a few named activity chips plus overflow count.
- Modal: richer fork list with actor/time/state.
- Strong visibility but high density and duplication.

Define `resolved` precisely, such as merged with no events after the merge watermark. Color is supplemental to text. Waiting or ready-to-merge attention outranks ordinary active styling.

## Updating review artifacts after feedback

When feedback replaces broad alternatives with a chosen direction:

- update the canonical plan and existing public pages in place;
- move the chosen behavior into **Confirmed decisions**;
- remove superseded direction selectors to avoid contradiction;
- preserve the established prototype and add new comparison sections only for newly undecided dimensions;
- keep plan and design pages separate and cross-linked;
- retain an explicit implementation gate until the user authorizes product changes.

## Verification

Run a focused temporary verifier after the final artifact edit. Check:

- every exact requested label appears;
- all alternatives exist on every requested surface;
- default/recommended option is selected consistently;
- interactive controls have handlers and accessible state;
- previous confirmed flows remain present;
- mobile rules avoid horizontal overflow;
- public pages return HTTP 200 and contain the amendment phrases.

Report this as ad-hoc artifact verification, not application-suite coverage.

## Pitfalls

- Mixing conversation status into the job status badge.
- Showing a full branch tree on a compact card.
- Treating “merged” as permanently resolved after new child activity.
- Merging raw transcripts without user review.
- Letting nested branches silently skip their direct parent.
- Leaving superseded alternatives beside a confirmed direction.
- Verifying before the final edit and citing stale evidence.

## Reference

See `references/conversation-branching-pattern.md` for a compact worked pattern covering editor navigation, multi-fork creation, parent merge, and progress surfaces.
