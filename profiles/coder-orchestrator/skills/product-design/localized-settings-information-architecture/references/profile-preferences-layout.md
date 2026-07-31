# Profile Preferences layout checklist

## Recommended order

1. Preferences page/card heading
2. App preferences
   - Language
   - Theme
   - Display currency
3. Notification preferences
   - Channel toggles
   - Event toggles
4. Explanatory footer text, if needed

Account remains separate and retains password, sign-out, security, and destructive account actions.

## Minimal implementation pattern

Reuse the existing controls and their persistence hooks. Move their rendered rows instead of introducing new state, wrappers, or duplicate components. If an existing internal section key such as `notifications` is already wired through props/tests, it may remain internal while every visible and accessible label becomes Preferences.

## Focused assertions

- Query the Preferences panel, then assert all three app-control groups are inside it.
- Compare DOM positions to prove app controls precede notification controls.
- Query the Account panel and assert those groups are absent.
- Assert Account still contains password and sign-out actions.
- Exercise language and currency independently; changing one must not reset the other.
- Run the same navigation-label check in every supported locale.

## Review wording

English:
- Preferences
- App preferences
- Notification preferences

Indonesian:
- Preferensi
- Preferensi aplikasi
- Preferensi notifikasi

Use natural localized descriptions rather than retaining old notification-only copy for the combined surface.
