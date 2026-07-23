---
name: code-change-verification
description: Verify code changes with fresh, accurately scoped evidence, including an ad-hoc fallback when no canonical command is detected.
---

# Code Change Verification

Use after modifying code and before reporting completion, committing, or deploying. The goal is evidence from the final workspace state, not merely a plausible implementation.

## Sequence

1. Prefer the repository’s documented canonical test, lint, and build commands.
2. Run the smallest existing regression test that directly exercises the changed behavior first.
3. Run broader canonical checks when available and proportionate to the change.
4. If code changes after a check, rerun the affected verification. Earlier output is stale evidence.
5. Capture fresh passing evidence before committing or reporting completion; do not rely on a build alone when the changed behavior needs a focused assertion.
6. Report exactly what ran and what passed. Do not convert a targeted pass into a claim that the whole suite is green.

For visual CSS changes, verification has two layers: mechanically assert the intended rule or computed relationship (for example, doubling an image aspect-ratio width halves its height at equal width), then obtain user visual approval when approval is part of the done definition. A successful build proves compilation, not visual correctness or approval.

## Ad-hoc fallback

When the environment does not detect a canonical verification command, run a focused ad-hoc check even if you already found and ran a build command manually. Build evidence and a targeted behavioral assertion are complementary; one does not replace the other.

1. Create a secure temporary script using the OS tempfile mechanism and a `hermes-verify-` prefix, for example:

```bash
verify_script=$(mktemp /tmp/hermes-verify-XXXXXX.sh)
```

2. Put the focused behavior check in that script. Prefer invoking an existing regression test over duplicating test logic.
3. Execute it against the actual changed code.
4. Remove the script afterward; use a cleanup trap when the script has multiple failure points.
5. Label the result “ad-hoc targeted verification.” State the behavior checked and distinguish passed tests from skipped tests.

The fallback supplements canonical checks; it does not redefine an arbitrary command as full-suite verification.

## Reporting examples

Good: “Ad-hoc targeted verification passed: the join-flow regression confirms users remain on program detail after joining; 35 unrelated tests were skipped.”

Bad: “All tests passed” when only one selected test ran.

## Existing-fix and same-route navigation verification

When the requested fix is already present in recent commits before you begin:

1. Inspect the exact commits and confirm both local `HEAD` and the tracked remote contain them; do not create a duplicate change or unnecessary commit.
2. Run the focused regression test and build from the current final workspace.
3. For “stay on this page” navigation bugs, assert the resulting pathname explicitly. A negative assertion such as “the sessions page is absent” is weaker and can pass after navigation to another wrong page.
4. If the handler canonicalizes an ID route to a slug route, verify that this same-detail-page replacement is intentional and test the canonical pathname, history behavior (`replace` versus `push`), and preserved page content.
5. For an already-deployed SPA, compare the public HTML’s asset hash with the live deployment and inspect or exercise the served asset/behavior. HTTP 200 alone does not prove the fix is deployed.
6. Report “already committed/pushed” rather than implying you made a new commit during the current run.

## Pitfalls

- Do not cite test/build output produced before the final edit.
- Do not use a predictable fixed filename under `/tmp`.
- Do not leave temporary verification artifacts in the repository.
- Do not claim deployment verification from a local test alone; probe the served artifact separately when deployment is part of the task.
- Do not equate a public HTML asset-name match with behavioral verification unless the deployed bundle is tied to the verified commit or the actual flow was exercised.
