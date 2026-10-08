# Public web artifact verification

Use this gate when a task is expected to finish with a deployed web UI.

## Gate

1. Build and test locally, but treat that only as source/build evidence.
2. Identify the actual deployment target and publish the artifact there. A Git push is not deployment unless the hosting pipeline is known and its completed run is verified.
3. Fetch the public route with a normal `GET`, not only `HEAD`/`curl -I`. Check the response body or rendered DOM for an app-specific marker; HTTP 200 alone can be a placeholder, health response, stale shell, or wrong virtual host.
4. Exercise the changed interaction on the public route. For controls, verify the real behavior (open, search, select multiple values, clear/remove values, URL/state update), not merely that matching source text exists.
5. Inspect browser console/network failures when available.
6. Report READY only after deployment and public interaction verification pass. If the route serves the wrong body or deployment mapping cannot be found, report the blocker and do not present the URL as the working app.

## Component-style pitfall

With scoped-style frameworks such as Svelte, a parent stylesheet selector may not match a class rendered inside a child component because scope attributes differ. Put responsive/layout rules in the child, expose a wrapper/class contract intentionally, or use the framework's explicit global/deep mechanism. Verify computed layout in the browser; a successful type check/build does not prove cross-component CSS applied.
