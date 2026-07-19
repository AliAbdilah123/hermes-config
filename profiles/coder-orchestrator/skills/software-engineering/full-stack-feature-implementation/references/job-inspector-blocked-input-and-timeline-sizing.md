# Job inspector blocked input and timeline sizing

Use when a job-detail inspector shows an unlabeled final control or an undersized event timeline.

## Identify the field before changing it

Trace the state guard and action endpoint. A control rendered only while `state === "blocked"` and submitted to an `input` action is not a generic comment field: it answers the agent's pending blocked-session request.

Label it explicitly (for example, **Blocked-session input**) and add a purpose-specific placeholder. Prefer a real wrapping `<label>` over relying only on `aria-label`; this fixes both visible comprehension and accessibility.

Keep this separate from an active-session comment composer. Comments are state-neutral conversation; blocked input may drive an explicit workflow transition.

## Give the timeline useful reading space

A `max-height` alone does not enlarge a short timeline; it only caps growth. Add a responsive minimum and retain a larger scrolling maximum, for example:

```css
.conversation {
  min-height: min(420px, 50dvh);
  max-height: 65dvh;
  overflow: auto;
}
```

Use `dvh` so the panel remains practical in mobile visual viewports. Keep the inspector itself scrollable so the larger timeline does not make controls unreachable.

## Verification

- Assert source/rendered markup includes the visible field label.
- Assert the timeline rule includes the intended responsive `min-height`.
- Run the native frontend tests and production build.
- Rebuild/restart an embedding backend if the SPA is embedded.
- Verify the live JS contains the label and live CSS contains the sizing marker.
- Wait for service readiness before curling after restart; `systemctl is-active` can become true just before the listener accepts connections.
