# Repository research report workflow

Use this for styled HTML reports that evaluate a public code repository: what it is, how to use it, effectiveness, costs, and use cases.

## Research before design

1. Pin the inspected repository state: owner/repo, commit SHA, tag/release, and access date.
2. Inspect README plus source-of-truth implementation files, manifests, tests, dependency locks, security policy, and release metadata. Do not infer capability from README positioning alone.
3. Separate three evidence classes throughout the report:
   - **Verified fact** — directly supported by source, manifest, execution, or official documentation.
   - **Assessment** — reasoned judgment based on verified facts.
   - **Not verified** — claims for which no outcome evidence was found.
4. Test the documented setup when practical. Report the exact verification boundary; never turn a failed local setup into a universal product claim.
5. Use official pricing sources for required runtimes/providers. Timestamp volatile figures.

## Required report sections

- Executive verdict: who should pilot it, and who should not rely on it yet.
- What it is and architecture.
- Exact installation and first-use workflow.
- Capability matrix showing implemented, experimental, disabled, and unverified surfaces.
- Effectiveness assessment:
  - executable evidence and tests;
  - adoption/maintenance signals;
  - missing outcome evidence such as case studies, lift, ROAS, CPA, or production scale.
- Cost model:
  - repository/license;
  - required model/runtime;
  - optional hosting/connectors/tools;
  - media or business operating spend kept separate;
  - low/medium/high scenarios with formulas and explicit assumptions.
- Strong-fit and poor-fit use cases.
- Security, privacy, maturity, and maintenance risks.
- A bounded pilot recommendation with measurable acceptance criteria.
- Clickable sources and access date.

## Cost discipline

Do not fabricate one all-in monthly number when usage is unknown. Show fixed costs separately from usage-based costs and use formulas such as:

```text
model cost = input tokens × input rate + output tokens × output rate + tool/cache charges
media cost = sum(platform daily budget × active days)
total = runtime + optional infrastructure + optional tools + media + tax
```

Do not automatically add subscription and API pricing; identify which execution path incurs which charge. Keep ad spend separate from software cost.

## Effectiveness discipline

- Stars, forks, downloads, and commits are interest/maintenance signals, not evidence of campaign or business outcomes.
- A broad test suite proves covered software behavior, not real-world effectiveness.
- Schema validity proves structure, not factual correctness.
- Disabled capabilities in machine-readable manifests override broad marketing language.
- Recommend a read-only pilot when live writes or outcome evidence are absent. Useful pilot measures include actionable-finding precision, false-positive rate, analyst time saved, recommendation agreement with an expert, and data-handling incidents.

## HTML shape

Produce one self-contained, responsive HTML file with semantic landmarks, table of contents, persistent theme toggle, print styles, accessible focus states, and no external dependency unless justified. Use visible labels for verified facts versus assessment. Prefer an editorial/technical design over generic SaaS cards.

## Verification and publication

Follow `references/prd-html-publication.md`. In addition:

- Parse/check the HTML and syntax-check embedded JavaScript.
- Verify theme persistence and viewport metadata.
- Verify source file permissions, symlink resolution, nginx config, local HTTP 200, and public HTTP 200.
- Browser visual inspection is preferred, but HTTP/static verification is still required and should be reported accurately if browser inspection is unavailable.

## Pitfalls

- Do not reproduce repository marketing claims without checking implementation manifests.
- Do not imply effectiveness from popularity.
- Do not hide disabled or experimental capabilities in footnotes.
- Do not mix software cost with advertising/media spend.
- Do not claim tests passed when dependency setup prevented execution.
- Do not let a temporary environment failure become a durable negative claim about the repository.
