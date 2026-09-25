# SPA Bundle Analysis Patterns for QA

Condensed patterns for inspecting deployed React/Vite/Next.js SPAs when the browser tool is unavailable or insufficient.

## Client Bundle URL Extraction

### Vite-style apps
HTML contains:
```html
<script type="module" src="/assets/index-HASH.js"></script>
<link rel="modulepreload" href="/assets/vendor-common-HASH.js">
```
The main `index-*.js` contains an inline chunk map. Extract chunk names with:
```
assets/([A-Za-z0-9_-]+\.js)
```
Download each chunk and concatenate.

### Next.js apps
Look for `/_next/static/chunks/` URLs or `next/dynamic` imports.

## Backend/Service URL Discovery

Client JS hardcodes service URLs. Search the combined corpus for:
- `https://...neon.tech/...auth` → Neon Auth
- `https://...supabase.co` → Supabase
- `https://...workers.dev` → Cloudflare Worker backend
- `https://...railway.app|render.com|fly.dev|vercel.app` → backend host
- Variables like `const m = w("URL", {adapter:...})` → auth client URL

## Auth Backend Detection

| String in bundle | Likely backend |
|---|---|
| `neonauth|neon.tech` | Neon Auth (fork of Better Auth) |
| `better-auth` | Better Auth |
| `createClient` + `supabase.co` | Supabase client |
| `collection|database|storage` + `appwrite` | Appwrite |
| `appId` + `meilisearch|elasticsearch|algolia` | search backend |

## Endpoint Enumeration

Extract with regex:
```python
re.findall(r'["\'](/api/[^"\']+)["\']', text)
re.findall(r'["\'](/app/[^"\']+)["\']', text)
```

Look for auth-specific paths:
- `/api/auth/sign-in/email`
- `/api/auth/sign-up/email`
- `/api/auth/get-session`
- `/api/auth/forgot-password`
- `/api/auth/sign-out`
- `/api/auth/two-factor/*`

## Feature Detection from Component Names

Component filenames in bundle paths:
| Filename pattern | Feature |
|---|---|
| `Login-*`, `Signup-*`, `ForgotPassword-*` | Auth pages |
| `DashboardPage-*` | Dashboard |
| `CalendarPage-*` | Calendar |
| `PostsPage-*` | Posts list |
| `CreatePostPage-*`, `EditPostPage-*` | Post CRUD |
| `AnalyticsPage-*` | Analytics |
| `SettingsPage-*` | Settings |
| `ThemeToggle-*` | Dark mode |
| `VideoCropModal-*` | Video cropping |
| `PaymentReturn-*`, `PaymentRedirect-*` | Payments |
| `PlansPage-*` | Pricing |

## Cookie-Based Auth Testing

```bash
# Login and capture cookies
curl -c cookies.txt -X POST https://host/api/auth/sign-in/email \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"..."}'

# Reuse for authenticated endpoints
curl -b cookies.txt https://host/api/analytics/overview
```

## Session-Specific Reference: Content Helper Apps

Sources:
- `brand-organizer`: `http://168.110.213.104/projects/brand-organizer/`
- `scheduling-post`: `https://scheduling-post.vercel.app`

Backends:
- Brand: custom `/api/auth/*` + `/api/analytics/*` + `/api/calendar/posts`
- Vercel: Better Auth on `https://ep-raspy-night-ai3v347f.neonauth.c-4.us-east-1.aws.neon.tech/neondb/auth`, data API on `https://content-factory-backend.baimbaru2022.workers.dev`

Brand API endpoints confirmed working:
- `/api/auth/sign-in/email` (cookie-based `brand_session`)
- `/api/auth/get-session`
- `/api/auth/sign-up/email`
- `/api/auth/forgot-password`
- `/api/auth/sign-out`
- `/api/analytics/overview`
- `/api/calendar/posts`
- `/api/instagram/accounts`
- `/api/plans`

Common pages in both apps:
- `/app/dashboard`, `/app/calendar`, `/app/posts`, `/app/posts/new`, `/app/analytics`, `/app/settings`, `/app/settings?tab=accounts`, `/app/plans`
