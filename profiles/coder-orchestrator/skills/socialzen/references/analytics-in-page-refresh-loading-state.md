# Analytics in-page refresh must preserve the mounted page

## Symptom

Clicking the Analytics page's own **Refresh** button appears to crash or blank the website, while a normal browser reload is unrelated and may work.

## Root cause pattern

The refresh flow performs two requests:

1. trigger provider analytics refresh;
2. fetch the updated analytics overview.

If step 2 reuses the initial page loader and sets the global `loading` state, the component replaces/unmounts the populated Analytics UI during the follow-up request. To users this looks like a page crash, especially when the overview request is slow.

## Minimal fix

Keep initial loading and background revalidation separate. The initial route load may show the full-page loading state; the post-refresh overview fetch must keep existing data/UI mounted.

A compact pattern is `load(background = false)`:

- only set/clear the full-page `loading` and initial `error` states when `background === false`;
- after a successful or partial provider refresh, call `load(true)`;
- keep the Refresh button's own `refreshing` state for progress/disabled behavior;
- do not hide a failed background fetch as a successful refresh—surface it through the refresh result/error UI if product behavior requires it.

## Regression test

Mock the initial overview as resolved, the refresh trigger as successful/partial, and the second overview request as permanently pending. Click **Refresh**, wait until the second overview request starts, then assert the existing Analytics UI and Refresh control remain mounted. This specifically fails when background revalidation toggles the full-page loading state.

## Verification

Run the focused Analytics page test, frontend typecheck, and production build. After deployment, exercise the in-page Refresh control and confirm the current analytics cards remain visible while refreshed data loads.
