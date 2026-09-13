# Selection-aware AI editing state

When selected editor text becomes one-shot AI message context, keep two distinct states:

1. **Pending message context** — the selected text shown in the drawer and embedded into the next request. Clear it immediately after that request is submitted.
2. **Captured edit target** — document identity plus selection range used by actions such as **Replace selection**. Retain it after submission until the response is applied or the target is invalidated.

Do not use one object for both responsibilities. Clearing one-shot context would also erase the range needed to apply the response.

Invalidate the captured target when:
- the active document changes;
- intervening edits make the range or selected text stale;
- the user explicitly dismisses the editing operation.

When replacement is unsafe, disable it and preserve a safe insertion fallback.

Focused verification:
- selected context is sent exactly once;
- the context card clears after submission;
- replacement remains available when the original target is still valid;
- replacement is disabled after document/range invalidation;
- insertion remains available after invalidation.
