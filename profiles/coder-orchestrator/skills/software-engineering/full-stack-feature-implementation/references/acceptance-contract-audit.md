# Acceptance-contract audit after autonomous implementation

Treat an autonomous coding agent's completion as a draft handoff.

1. Mechanically compare the component hierarchy and API response contract against every explicit acceptance item before testing or accepting the implementation.
2. Reject semantic substitutes (for example, a generic pipeline widget in place of specifically named KPI cards), omitted sections, changed ordering, or extra management surfaces.
3. When asked to reuse an **existing** subsystem (Activities, CRM, tasks, onboarding, etc.), first identify its current route, page, tables, handlers, and visual component. Do not create a new subsystem and call it existing.
4. If no matching UI exists but canonical underlying records do, add only the minimum read surface needed and report that distinction.
5. A focused source-contract test may assert required labels/order, but pair it with backend contract tests and exact-route rendered/browser verification; source strings alone do not prove behavior.
6. If the user requests low token usage, keep progress and final reports terse without relaxing implementation or verification gates.
