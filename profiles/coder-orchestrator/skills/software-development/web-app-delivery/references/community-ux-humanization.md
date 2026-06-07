# Community UX Humanization Reference

Use this when a deployed web app technically works but feels like a corporate dashboard or internal CRM.

## Goal

Shift the primary experience from data/admin-first to people/action-first while preserving the existing backend and behavior.

## Practical rewrite pattern

1. **Keep behavior stable**
   - Preserve data types, API base path detection, fetch/action handlers, admin token/session storage, and mutation action names.
   - Avoid backend/schema changes unless the user asks for new product behavior.

2. **Make the home screen answer user questions**
   - What is happening soon?
   - What can I do right now?
   - Who needs attention/help?
   - What do I already have booked or available?

3. **Replace corporate language**
   - Dashboard/Command → Today/Home
   - Programs → Circles/Communities
   - Sessions → Events
   - Wallet → My passes
   - Commerce → Memberships
   - Analytics → Admin insights
   - Audit → Safety log

4. **Add people-first modules**
   - Warm welcome hero with current actor/user.
   - Quick actions: book, join, gift/help, approve/respond.
   - Upcoming event/session card.
   - Community pulse/feed from notifications/activity.
   - Member wallet/pass highlights.
   - Organizer metrics/admin surfaces moved later in nav.

5. **Visual treatment**
   - Softer colors, rounded cards, stronger whitespace, mobile-first grids.
   - Replace dense statistic grids as the first impression; keep stats lower on the page or in admin tabs.

## Verification checklist

- `npm run build` passes.
- Built assets are deployed to the nginx project path.
- Nginx frontend returns `200 text/html`.
- Project API bootstrap still returns valid JSON.
- Headless DOM smoke contains new user-facing copy such as the new hero, quick action, and feed labels.
- If public-IP curl times out from the host, verify localhost nginx and Tailscale/local network separately and report the hairpin/network caveat honestly.
