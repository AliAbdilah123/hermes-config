# Detail Column With Mobile Preservation

## Session-derived pattern

A desktop calendar used two columns: a selected-session/list panel and the calendar. The selected-session content was initially wrapped in its own bordered details panel inside the already bordered first column. User feedback identified this as a “box inside box.”

The correct refinement was structural:

- Keep the first column as the panel.
- Remove the inner details wrapper from the component markup.
- Render the selected-session product pill, date, facts, voucher/package options, and booking row directly at column level.
- Increase desktop detail typography because compact card sizing no longer suits a full column.
- Keep the initial empty state in that column, prompting selection from the calendar.

## Example scoped hierarchy

Useful prototype scale (adapt to project tokens):

- selected title: about 30px
- date: about 17px
- facts: about 16px with relaxed line-height
- subsection heading: about 20px
- choice labels: about 14–15px

Scope these rules beneath the desktop list-panel selector. Do not modify shared detail selectors globally.

## Explicit mobile exclusion

The mobile prototype retained a separate upcoming-session/filter mechanism. “Do not change mobile” overrode any temptation to propagate the desktop deprecation there. Preserve the mobile component tree, controls, and styles exactly while refining desktop.

## Ad-hoc verification checklist

Use a temporary `/tmp/hermes-verify-*` script to assert:

- the obsolete inner details wrapper is absent from the page component;
- the desktop first-column/list-panel class remains present;
- larger typography rules are namespaced beneath that first-column selector;
- the mobile review/list component markers remain present.

Clean up the script and describe the evidence as targeted ad-hoc verification. Separately run the real build and verify the public route returns HTTP 200 before sharing the prototype link.
