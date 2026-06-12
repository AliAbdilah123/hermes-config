# Frontend navigation/auth refinement pattern

Use this when refining an already-deployed marketplace or B2C app where the user asks for clearer public landing, login/signup entry, and profile navigation.

## Implementation notes

- Keep public discovery content visible without authentication: hero, service cards, categories, and "services needed"/posting categories should render before login.
- Move demo-account login helpers out of the public page body when the user asks for a cleaner nav login. Put login/signup in a modal or dedicated route opened from the header.
- Make the header auth state explicit:
  - Logged out: clear `Login / Masuk` / signup entry point.
  - Logged in: avatar button with `aria-haspopup`, `aria-expanded`, user name/email, role badges, dashboard navigation, profile page navigation, and logout.
- Route "Dashboard" to the best existing role-aware surface instead of inventing a fake page: admin console for admins, provider jobs for providers, home/customer dashboard for customers.
- Add a real profile page or disable the menu item; do not leave profile navigation as a placeholder.
- Preserve existing API paths, token storage, session refresh, and role checks unless the user explicitly asks to redesign auth.

## Test/verification notes

- Add tests that public landing content is present while logged out and role-restricted labels are absent.
- Assert demo login labels are not visible on the public landing until the login modal opens.
- Test the header login button opens the login/signup UI.
- For an authenticated mock, click the avatar and assert name, roles/actions, Dashboard, Profile page, and Logout are visible.
- After deployment, verify through the serving layer, not only Vite build:
  - frontend route returns 200
  - project-prefixed API returns real public data
  - headless DOM includes key public landing, login, services, and services-needed strings
  - capture/inspect a screenshot when layout/visual changes matter
