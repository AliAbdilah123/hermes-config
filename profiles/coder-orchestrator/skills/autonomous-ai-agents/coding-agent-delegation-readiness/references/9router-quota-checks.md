# 9Router quota checks

Use this reference when the user asks for quota remaining from a local 9Router instance.

## Discovery

- Locate the executable with `command -v 9router` and inspect the running process for its port; the common default is `20128`.
- The root may redirect or return `/dashboard`.
- Confirm auth state with `GET /api/auth/status` before probing protected endpoints.

## Codex quota path

The dashboard quota page calls these endpoint families:

- `GET /api/providers/client?...` to identify provider connections.
- `GET /api/usage/<provider-id>` for current usage/quota.
- `POST /api/usage/<provider-id>/codex-reset-credits` changes state; never call it merely to inspect quota.

Exact query parameters can vary by 9Router release, so inspect the installed quota-page bundle or browser network traffic rather than guessing IDs.

## Authentication and reporting

- A `401 Unauthorized` means the dashboard requires an authenticated cookie/session; it does not mean quota is unavailable.
- Prefer reusing an existing authenticated browser session. Otherwise ask for the dashboard password, authenticate, then read the quota endpoint.
- Report the displayed rolling-window/weekly percentages and reset times verbatim, including which Codex connection they belong to when multiple connections exist.
- Do not substitute Codex TUI context percentage, model label, process startup, or local request logs for 9Router quota remaining.
