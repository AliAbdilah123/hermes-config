---
name: dogfood
description: "Exploratory QA of web apps: find bugs, evidence, reports."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [qa, testing, browser, web, dogfood]
    related_skills: []
---

# Dogfood: Systematic Web Application QA Testing

## Overview

This skill guides you through systematic exploratory QA testing of web applications using the browser toolset. You will navigate the application, interact with elements, capture evidence of issues, and produce a structured bug report.

## Prerequisites

- Browser toolset must be available (`browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, `browser_vision`, `browser_console`, `browser_scroll`, `browser_back`, `browser_press`)
- A target URL and testing scope from the user

## Inputs

The user provides:
1. **Target URL** — the entry point for testing
2. **Scope** — what areas/features to focus on (or "full site" for comprehensive testing)
3. **Output directory** (optional) — where to save screenshots and the report (default: `./dogfood-output`)

## Workflow

Follow this 5-phase systematic workflow:

### Phase 1: Plan

1. Create the output directory structure:
   ```
   {output_dir}/
   ├── screenshots/       # Evidence screenshots
   └── report.md          # Final report (generated in Phase 5)
   ```
2. Identify the testing scope based on user input.
3. Build a rough sitemap by planning which pages and features to test:
   - Landing/home page
   - Navigation links (header, footer, sidebar)
   - Key user flows (sign up, login, search, checkout, etc.)
   - Forms and interactive elements
   - Edge cases (empty states, error pages, 404s)

### Phase 2: Explore

For each page or feature in your plan:

1. **Navigate** to the page:
   ```
   browser_navigate(url="https://example.com/page")
   ```

2. **Take a snapshot** to understand the DOM structure:
   ```
   browser_snapshot()
   ```

3. **Check the console** for JavaScript errors:
   ```
   browser_console(clear=true)
   ```
   Do this after every navigation and after every significant interaction. Silent JS errors are high-value findings.

4. **Take an annotated screenshot** to visually assess the page and identify interactive elements:
   ```
   browser_vision(question="Describe the page layout, identify any visual issues, broken elements, or accessibility concerns", annotate=true)
   ```
   The `annotate=true` flag overlays numbered `[N]` labels on interactive elements. Each `[N]` maps to ref `@eN` for subsequent browser commands.

5. **Test interactive elements** systematically:
   - Click buttons and links: `browser_click(ref="@eN")`
   - Fill forms: `browser_type(ref="@eN", text="test input")`
   - Test keyboard navigation: `browser_press(key="Tab")`, `browser_press(key="Enter")`
   - Scroll through content: `browser_scroll(direction="down")`
   - Test form validation with invalid inputs
   - Test empty submissions

6. **After each interaction**, check for:
   - Console errors: `browser_console()`
   - Visual changes: `browser_vision(question="What changed after the interaction?")`
   - Expected vs actual behavior

### Phase 3: Collect Evidence

For every issue found:

1. **Take a screenshot** showing the issue:
   ```
   browser_vision(question="Capture and describe the issue visible on this page", annotate=false)
   ```
   Save the `screenshot_path` from the response — you will reference it in the report.

2. **Record the details**:
   - URL where the issue occurs
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Console errors (if any)
   - Screenshot path

3. **Classify the issue** using the issue taxonomy (see `references/issue-taxonomy.md`):
   - Severity: Critical / High / Medium / Low
   - Category: Functional / Visual / Accessibility / Console / UX / Content

### Phase 4: Categorize

1. Review all collected issues.
2. De-duplicate — merge issues that are the same bug manifesting in different places.
3. Assign final severity and category to each issue.
4. Sort by severity (Critical first, then High, Medium, Low).
5. Count issues by severity and category for the executive summary.

### Phase 5: Report

Generate the final report using the template at `templates/dogfood-report-template.md`.

The report must include:
1. **Executive summary** with total issue count, breakdown by severity, and testing scope
2. **Per-issue sections** with:
   - Issue number and title
   - Severity and category badges
   - URL where observed
   - Description of the issue
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshot references (use `MEDIA:<screenshot_path>` for inline images)
   - Console errors if relevant
3. **Summary table** of all issues
4. **Testing notes** — what was tested, what was not, any blockers

Save the report to `{output_dir}/report.md`.

## Tools Reference

| Tool | Purpose |
|------|---------|
| `browser_navigate` | Go to a URL |
| `browser_snapshot` | Get DOM text snapshot (accessibility tree) |
| `browser_click` | Click an element by ref (`@eN`) or text |
| `browser_type` | Type into an input field |
| `browser_scroll` | Scroll up/down on the page |
| `browser_back` | Go back in browser history |
| `browser_press` | Press a keyboard key |
| `browser_vision` | Screenshot + AI analysis; use `annotate=true` for element labels |
| `browser_console` | Get JS console output and errors |

## Support Files
- `references/issue-taxonomy.md` — severity/category taxonomy for bug reports
- `references/spa-bundle-analysis-patterns.md` — static JS-bundle inspection patterns, backend discovery, cookie-based authenticated testing, and Content Helper (brand-organizer / scheduling-post) reference endpoints
- `templates/dogfood-report-template.md` — report template for Phase 5 output

## Fallback: Browserless SPA Testing via Bundle Analysis

Symptom: `browser_navigate` times out repeatedly on a React/Vite/Next.js SPA, even after multiple retries.

Pivot: Do not keep retrying the browser. Switch to a `curl` + static bundle inspection workflow.

1. Fetch the HTML entrypoint with `curl` and extract all `<script type="module" src="...">` and `<link rel="modulepreload" ...>` URLs.
2. Download each JS chunk and concatenate the source into one analysis corpus (save to `/tmp/<site>.js` for inspection).
3. From the combined JS:
   - Extract all hardcoded `https://...` URLs (often reveal backend/service URLs).
   - Extract all route-like strings (e.g. `/app/...`, `/api/...`).
   - Search for feature keywords: auth methods, third-party integrations, component names.
4. Reconstruct the endpoint map **from the client bundle**, not from the network.

This workflow works when the browser stack is blocked by CSP, WASM startup, or Cloudflare in your execution environment.

## Feature Comparison Between Two Deployed SPAs

Use this when the user asks "what feature does app A have that app B doesn't?" for two deployed SPAs.

### Step 1 — Get working instruments
- If one app needs creds, try a programmatic login via curl first:
  ```
  curl -X POST https://host/api/auth/sign-in/email \
    -H 'Content-Type: application/json' \
    -d '{"email":"...","password":"..."}'
  ```
- Capture the `Set-Cookie` header and reuse with `curl -b "cookie_name=value"` for subsequent authenticated endpoints.

### Step 2 — Build comparable feature tables
- Count component/page names (e.g. `DashboardPage`, `CalendarPage`, `VideoCropModal`).
- Count explicit API paths like `/api/auth/get-session`, `/api/posts/media`.
- Count auth plugins: better-auth plugins (`two-factor`, `magic`), social providers (`google`, `github`, `facebook`).
- Count bot-protection integrations: `turnstile`, `recaptcha`.
- Count route strings in client router.

### Step 3 — Identify nose gaps
A feature gap is a feature present in the "reference" app but absent in the "target" app. Focus on:
- Authentication/2FA hardening
- Subscription/payment lifecycle API endpoints
- Profile/avatar APIs
- Growth/experimentation endpoints (`product_tours`, `surveys`, `web_experiments`)
- Protected API surfaces the client bundle references even if the server is inaccessible

## Tips

- **Always check `browser_console()` after navigating and after significant interactions.** Silent JS errors are among the most valuable findings.
- **Use `annotate=true` with `browser_vision`** when you need to reason about interactive element positions or when the snapshot refs are unclear.
- **Test with both valid and invalid inputs** — form validation bugs are common.
- **Scroll through long pages** — content below the fold may have rendering issues.
- **Test navigation flows** — click through multi-step processes end-to-end.
- **Check responsive behavior** by noting any layout issues visible in screenshots.
- **Don't forget edge cases**: empty states, very long text, special characters, rapid clicking.
- When reporting screenshots to the user, include `MEDIA:<screenshot_path>` so they can see the evidence inline.
- **Browser tool failure is not always a test blocker.** When `browser_navigate` times out on a JS-heavy app, pivot to `curl` + JS-bundle strategy; it often reveals more of the backend surface area than UI-only testing.
- **When comparing two SPAs, prefer feature parity analysis via bundle inspection** instead of hand-clicking both apps.
- **Auth server discovery**: client JS often hardcodes the auth backend URL. Search for `https://...neon.tech`, `supabase.co`, `pocketbase`, or variables containing `/auth`.
