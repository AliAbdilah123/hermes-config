# Public preview host routing and page-identity verification

Use this when a preview artifact is published under a shared `/prd/...` alias but the product also has one or more custom domains.

## Risk

A URL can return HTTP 200 while serving the product SPA fallback instead of the preview artifact. This is common when the shared nginx `/prd/` alias exists on a documentation or development host but not on the product's custom production host. Headless screenshots then look valid yet depict the login or landing screen rather than the intended prototype.

## Verification sequence

1. Publish the artifact to the configured preview root and set readable file permissions.
2. Probe every plausible public host with the **exact deep path**.
3. Do not accept status alone. Fetch the response body and assert a stable artifact identity marker such as its unique `<title>`, heading, or explicit build marker.
4. Prefer the host whose response contains that marker. Treat another host returning a product shell, login page, or unrelated SPA as a routing miss even when it returns 200.
5. Capture desktop and mobile screenshots from the verified host, each with a fresh cache-busting query.
6. Require non-empty screenshot files, inspect the pixels, and confirm the page identity again from visible unique content.
7. Share only the verified deep links. State that production is unchanged when the artifact is review-only.

## Minimal shell probe

```sh
body=$(curl -fsSL "https://HOST/prd/ARTIFACT/?verify=$(date +%s%N)")
printf '%s' "$body" | grep -Fq '<title>UNIQUE ARTIFACT TITLE</title>'
```

Use a semantic identity marker rather than a byte-count threshold whenever possible. A large fallback SPA can easily satisfy a size check.

## Pitfall

Do not infer that a product's canonical domain inherits the server's shared `/prd/` route. Virtual hosts can have different nginx location blocks and fallbacks. Verify host + route + body identity as one unit before browser QA.
