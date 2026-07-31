---
name: localized-settings-information-architecture
description: Organize localized profile/settings navigation so app preferences, notification preferences, and account/security actions remain clear, non-duplicated, and verifiable.
version: 1.0.0
---

# Localized Settings Information Architecture

## Use when

Use when creating or refining a multilingual profile/settings area, especially when controls are being renamed or moved between tabs.

## Information architecture

1. Name the combined app-settings surface **Preferences** in English and use the natural locale equivalent (for Indonesian, **Preferensi**).
2. Put app-level controls first: language, display currency, and light/dark theme.
3. Put notification-channel or notification-event toggles below them in a clearly titled **Notification preferences** subsection.
4. Reserve **Account** for password, sign-out, security, deletion, and other account actions.
5. Remove moved controls from their old surface. Do not leave duplicate controls merely for compatibility.
6. Preserve an established internal section ID or route when renaming it adds migration risk without user benefit. Visible labels, headings, and accessible names must reflect the new information architecture.

## Localization quality

- Translate the meaning of the combined surface, not the old technical name.
- Keep labels concise and natural in each language.
- In conversational Indonesian, use **Preferensi**, avoid document-like passive phrasing, avoid **Anda**, and use **kamu** only where a pronoun is genuinely needed.
- Keep product terminology consistent with the surrounding application.

## Test-first regression contract

Write the focused UI test before moving production markup and observe the expected failure. Verify:

1. The sidebar exposes the new localized Preferences label, not the old Notifications label.
2. Language, theme, and display-currency controls appear in Preferences before notification toggles.
3. Those controls are absent from Account.
4. Password and sign-out actions remain in Account.
5. Language and display currency persist independently across tab changes and reloads.
6. English and secondary-language headings and accessible labels are correct.

## Public verification boundary

For authenticated settings, a redirect to sign-in is not feature evidence. Exercise a preview-safe authenticated session, open Preferences through normal navigation, change each app preference, reload, and verify persistence and independence. If authentication cannot be completed, report **public authenticated E2E pending**; tests, builds, HTTP 200, screenshots of sign-in, and deployed-bundle strings do not make the flow ready for approval.

## Supporting detail

See `references/profile-preferences-layout.md` for a compact implementation and review checklist.

## Pitfalls

- Renaming only the heading while leaving the sidebar or accessible name as Notifications.
- Moving controls visually but leaving duplicate controls in Account.
- Mixing password/security actions into general app preferences.
- Renaming stable internal IDs unnecessarily and breaking deep links or tests.
- Claiming public E2E from a protected route that only rendered sign-in.
