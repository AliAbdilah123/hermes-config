# Social Notes example

## Detail

Initial note fetch must not call social-provider resolution. If a usable URL or attachment reference exists, show **Load post**. Activation owns loading/error/retry and guards duplicate clicks. Cached media renders only after explicit activation.

## List and filters

- Default search scope: title and body.
- Multi-source and multi-tag values use repeated URL/API keys.
- Read URL state on mount and `popstate`; reject stale async responses with a request generation ID.
- Show row tag chips and removable active-filter chips.
- Keep controls wrapping without horizontal overflow at narrow mobile widths.

## Selection and bulk actions

- Select rows individually or all records on the visible page.
- Clear IDs no longer visible after filter/page/result changes.
- Export selected visible notes in visible order as one Markdown document with title, source, timestamps, optional tags, body, and separators.
- Confirm once, delete sequentially through the existing endpoint, collect failures, refresh, retain failed selections, and report the partial failure.

## Focused assertions

- `searchParams.getAll('source')` and `getAll('tag')` retain repeated values.
- Initial detail flow contains zero provider resolve calls.
- Export tests cover Markdown escaping and absent tags.
- Partial delete tests prove success IDs clear and failed IDs remain.
- Final evidence includes tests, static/type check, and production build.
