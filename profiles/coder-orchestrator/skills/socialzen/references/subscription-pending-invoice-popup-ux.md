# Pending subscription invoice popup UX

When the user asks to make the unpaid invoice reminder more visible, keep this as a UI-only change if `/api/subscription/status` already returns `pendingPlanChange`.

## Pattern

- Render pending invoice reminders as a fixed card, not a thin top banner.
- Desktop/tablet: bottom-right card, about `w-[min(92vw,520px)]`, high z-index, rounded border, shadow.
- Mobile: center the card in the viewport with `fixed inset-x-4 top-1/2 -translate-y-1/2`.
- Copy should ask the decision explicitly: continue the earlier invoice subscription or reject it.
- Persistence must come from backend state (`pendingPlanChange` / saved pending invoice fields), not localStorage/session UI state. The card should survive refreshes and polling until the user clicks Continue or Reject.
- Continue should call `/api/subscription/continue` and redirect to the saved payment URL.
- Reject should call `/api/subscription/reject`, which clears pending invoice fields.

## Verification

- `pnpm typecheck`
- `pnpm build`
- Grep deployed bundle for stable popup copy such as `Unpaid subscription invoice`.
- Verify JS asset content type is `application/javascript` after deploy so Cloudflare/nginx did not cache an HTML fallback.
