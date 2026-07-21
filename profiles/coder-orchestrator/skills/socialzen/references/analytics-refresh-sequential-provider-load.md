# Analytics refresh: sequential provider load and false “crash” reports

Use when SocialZen stays visible or appears to crash/freeze after clicking the Analytics page's in-page **Refresh** button, especially after a frontend loading-state fix already passed tests.

## Do not stop at frontend rendering

A component test proving that Analytics remains mounted only verifies presentation. Before declaring the bug fixed, exercise or inspect the real refresh path and measure the backend work. Build success and a JavaScript asset `200` are not evidence that the refresh operation completes promptly.

## Root-cause checklist

1. Inspect recent `analytics_refresh` service logs for provider failures and request timing.
2. Count published `post_targets` for the affected user, grouped by platform.
3. Read `analyticsRefresh` and count external requests per target:
   - Instagram commonly performs basic metrics plus insights requests.
   - Facebook may perform engagement plus insights requests.
   - Threads performs its own insights request.
4. Check whether targets are processed sequentially and note the configured HTTP-client timeout.
5. Estimate the worst-case request duration: target count × provider calls × timeout. A moderate account can turn one refresh into dozens of serialized Meta calls.
6. Identify provider-invalid metric combinations. For example, Meta may reject `impressions` for particular Instagram media product types; repeatedly requesting an unsupported metric adds latency and predictable partial failures.
7. Distinguish these layers explicitly:
   - frontend unmount/render crash;
   - browser/API timeout or apparent freeze;
   - backend sequential workload;
   - provider metric rejection.

## Safe fix direction

- Keep stale analytics visible during refresh.
- Bound provider refresh concurrency rather than launching unbounded goroutines.
- Preserve exact `post_target_id` isolation and collect deterministic per-target results.
- Never perform concurrent DB work while holding open SQLite rows; materialize targets and close the cursor first.
- Avoid or retry without metrics known to be unsupported for that media/product type, preserving unavailable values as `NULL` rather than zero.
- Apply request-scoped/provider timeouts and cancellation so one slow destination cannot monopolize the entire refresh.
- Consider an asynchronous refresh job with polling/status when the bounded operation still exceeds a normal HTTP interaction window.

## Verification

1. Add a failing backend regression/performance test before changing production code.
2. Cover multiple delayed targets and assert bounded completion/concurrency.
3. Cover an unsupported Instagram insight metric and assert a useful partial result without repeatedly paying for the same invalid request shape.
4. Run targeted Go tests and build.
5. Exercise the real authenticated in-page refresh against representative target counts while timing the request.
6. Check browser console/network and service logs after the click.
7. Only then deploy, verify the public flow, commit, and push.

## Reporting pitfall

Do not tell the user the issue is fixed solely because a mocked frontend test, typecheck, build, deployment, and asset probe passed. Report which layer was verified and keep investigating if the user-visible refresh itself was not exercised.
