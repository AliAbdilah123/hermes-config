---
name: komuna-daily-report
description: "Use when the user asks Hermes to prepare today's Komuna daily report/status update from prior project progress and today's planned work. Enforces the exact report template, date rules, Discord/session-search constraints, and mandatory clarification before generating the report."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [komuna, daily-report, status-update, discord, session-search]
    related_skills: [hermes-agent]
---

# Komuna Daily Report

## Overview

Use this skill whenever the user asks for a daily report, daily standup, work report, or status update for the Komuna project. The report must be written for the current user and for today, unless the user explicitly asks for a different reporting date.

The agent must strictly follow the user's template and must not generate the final report until it has asked a clarifying question about what the user will do today.

## Required Report Template

Use exactly this structure:

```text
What I did yesterday:
1. 

What challenge(s) I found yesterday:
1. 

What I will do today:
1. 
```

If the reference day is last Friday because today is Monday, change the first two headings to:

```text
What I did last Friday:
1. 

What challenge(s) I found last Friday:
1. 

What I will do today:
1. 
```

If the user asks for a specific different date for the previous-progress section, adapt the heading wording to that date while keeping the same three-section template.

## Date Rules

1. Default behavior:
   - If today is not Monday, the "yesterday" sections refer to the exact previous calendar day.
   - If today is Monday, the "yesterday" sections refer to last Friday and the heading wording must say "last Friday" instead of "yesterday".
2. Monday weekend merge:
   - On Monday, search last Friday's Komuna progress.
   - If there was progress on Saturday or Sunday, summarize that weekend progress into the last Friday progress section.
3. User-specified date:
   - If the user specifically asks for a different date for the previous-progress section, use that date instead of the default yesterday/Monday rule.

## Progress Discovery Rules

1. Prefer Discord/channel context if available:
   - Search only previous chats and threads in the current channel/chat.
   - Do not use unrelated channels or unrelated project conversations.
2. If direct Discord history access is not available:
   - Use `session_search` to find related agent sessions for the relevant date.
   - Determine today's actual date first from runtime/current system date, then derive yesterday/last-Friday/reference dates.
   - Search sessions updated/active within the last 3 calendar days from today, not only sessions created on the target date.
   - Inspect promising older Komuna sessions in that 3-day window because chats/messages from yesterday can occur inside an older session.
   - Filter evidence by the date of the message/chat content whenever available; do not discard a session solely because its session start date is older.
   - Restrict findings to Komuna only.
   - Exclude other project sessions.
3. Use only evidence from:
   - The current user's prompt.
   - Relevant Komuna sessions/chats for the requested date range.
4. Do not invent progress or challenges.

## Categorization Rules

When the user adds new progress in the prompt:

1. Add it to the previous-progress section unless the user clearly says it is for today.
2. Categorize each item as either:
   - Accomplishment: goes under `What I did yesterday` / `What I did last Friday`.
   - Difficulty/challenge: goes under `What challenge(s) I found yesterday` / `What challenge(s) I found last Friday`.
3. If the user does not specify the type, infer the category from the wording.
4. If the user appears to have no difficulties, omit challenge items rather than inventing them. If the section would be empty, either omit the challenge line items or write no challenge section only if the user/project convention allows; otherwise leave it empty after the heading.

## Mandatory Clarification Before Final Report

Before generating the final report, always ask the user what they will do today.

Rules:

1. Do not generate the report before asking this clarifying question.
2. The user does not need to provide a polished sentence; accept rough notes or fragments.
3. Format the user's answer into the `What I will do today` section.
4. If the user already specified or implicitly mentioned today's tasks, ask a follow-up clarification such as:
   - "Do you want me to include that in the `What I will do today` section?"
5. If there are no progresses for the previous day/reference day and the user did not provide previous activity, ask what they did and what difficulties they had for that day.
6. If the user omits either accomplishments or difficulties, categorize what they gave and do not force a difficulty if none is shown.

## Workflow

1. Determine the report date and reference progress date:
   - Today by current system date unless user specifies otherwise.
   - Apply Monday/last-Friday/weekend merge rules.
2. Gather Komuna-only previous progress:
   - First determine today's actual date from the runtime/current system date. Do not guess from memory or session IDs.
   - Search current-channel/chat history if available.
   - If not available, use `session_search` for Komuna sessions around the relevant date.
   - Also check recent chat messages inside Komuna sessions that are no more than 3 calendar days old from today, because an older session can contain new chats/messages from the target day. Filter by message/chat date, not only by session creation date.
3. Parse the user's prompt for additional progress or challenges.
4. Categorize discovered items into accomplishments and challenges.
5. Before writing the report, ask the user what they will do today, or clarify whether already-mentioned today tasks should be included.
6. After the user answers, generate the final report using the exact template.

## Session Search Strategy for Progress Discovery

### Multi-Pass Search

Session search is imprecise — use a multi-pass approach, not a single query:

1. **First pass — broad Komuna query:** `session_search(query="komuna", sort="newest", limit=5)` — catches most sessions.
2. **Second pass — topic-specific terms:** Search for work items mentioned by the user: `query="xendit OR sort OR card OR seed OR product OR voucher"` — catches sessions where "komuna" keyword didn't appear in the FTS5 snippet but the work is Komuna-related.
3. **Third pass — browse all recent:** `session_search()` with no query — returns recent sessions chronologically. Check the `source` field to filter for the right Discord user (e.g., "Goresan Abadi" — "Capt4ce" is a different user).
4. **If the user disputes your findings, trust them and dig harder.** Do not argue that "only one session was found." Expand to broader queries, scroll into promising sessions, and check session `started_at` timestamps against the target date.

### UTC Session ID vs WIB Date Boundaries

**CRITICAL:** Session IDs use UTC timestamps (e.g., `20260702_031901` = July 2 03:19 UTC). The user is in WIB (UTC+7). A session with ID `20260702` (July 2) may have actually started on July 1 afternoon WIB. Always check the `started_at` field (epoch timestamp) and the `when` display field, not just the session ID prefix, when filtering by calendar date.

Example: Session `20260702_031901` shows `when: "July 02, 2026 at 03:19 AM"` but `started_at: 1782898462` = July 1 ~16:34 WIB. This was July 1 work, not July 2.

### Compacted Sessions Hide Content

Sessions with 100+ messages get context-compacted. The FTS5 snippet in `session_search` results only shows text near the match, which may be a compaction summary — not the actual work done. When a session looks promising but its snippet only shows compaction boilerplate:

1. **Scroll into the session** with `session_search(session_id=..., around_message_id=...)` to read the actual user messages and assistant summaries.
2. **Read the full session** with `session_search(session_id=...)` (no around_message_id) to get the first 20 + last 10 messages, which often contain the final summary.
3. Look for assistant-produced summaries like "Here's what changed" / "Final state" tables — these are the best evidence of actual work.

### De-duplicating Across Sessions

Sessions in the daily report session itself (the `komuna-daily-report` skill invocation) are NOT yesterday's work — they're today's report preparation. Exclude the current daily-report session from progress discovery.

Cross-reference session IDs: if the same session appears in multiple searches, it's the same work — don't double-count it as multiple items.

### Commit Cross-Check for Komuna Daily Reports

When the user asks for a thorough daily report, disputes that the findings are too small (e.g. "only that?"), or asks to include commits, cross-check the Komuna repo in addition to session history:

1. Run `git log --all --since='<reference-date> 00:00:00 +0000' --until='<reference-date> 23:59:59 +0000' --date=iso --pretty=format:'%h%x09%ad%x09%s' --no-merges` from `/home/ubuntu/projects/komuna`.
2. Use commit subjects as leads for additional session searches, especially when the work occurred inside older/compacted sessions.
3. Correlate commits with user/assistant final summaries from July 9-style sessions; do not list commits alone as accomplishments unless they match Komuna chat evidence or clear commit messages.
4. Include challenge evidence from root-cause/final summaries, not fabricated difficulty.
5. Still ask for today's plan before generating the final report.

## Common Pitfalls

1. Generating the report immediately without asking today's plan. This violates the user's explicit instruction.
2. Mixing projects. Only Komuna-related progress belongs in the report.
3. Treating Monday as Sunday. On Monday, use last Friday and summarize weekend work into that section if any exists.
4. Inventing challenges. If no difficulty is evident, do not fabricate one.
5. Over-polishing into a different template. Keep the exact heading structure and numbered list format.
6. Searching broad history without project filtering. If using `session_search`, query for Komuna-specific terms and ignore unrelated projects.
7. **Trusting session ID dates over actual timestamps.** Sessions with tomorrow's UTC date may have started today in WIB.
8. **Relying on FTS5 snippets from compacted sessions.** Snippets may show compaction boilerplate instead of actual work — scroll into the session to read the real content.
9. **Single-query session search.** One `query="komuna"` search misses sessions where the work is Komuna but the snippet doesn't contain the keyword. Always do a second pass with topic-specific terms.
10. **Arguing with user corrections.** If the user says "I did more than that," they're right. Run broader searches, scroll into sessions, and find the missing work.

## Verification Checklist

- [ ] Correct reference day applied: yesterday, last Friday, or user-specified date.
- [ ] Komuna-only progress used.
- [ ] Additional user-provided progress categorized correctly.
- [ ] Today's plan clarification asked before final report.
- [ ] Final output uses the exact required structure.
- [ ] No invented progress or challenges.
