# Discovery hero program carousel prototype

Use this pattern when a Komuna Discovery prototype needs rotating program imagery in the hero while production implementation remains approval-gated.

## Data and route fidelity

- Use actual program records from Komuna's SQLite/API: `id`, `name`, `location`, and `image_url`.
- Link each slide to the real public route `/programs/<id-or-slug>`; verify every target returns HTTP 200.
- Use each program's real root-relative image URL (for example `/program-images/prog-box.svg`), resolved against the public Komuna origin.
- Do not fabricate promotional labels, ratings, or scarcity. Neutral labels such as “Featured program” are acceptable only when the corresponding program is genuinely featured.

## Minimal interaction model

- Render slides as anchors so the entire image/card is keyboard-accessible and navigates without JavaScript.
- Rotate with one `setInterval`; a 4-second interval is a reasonable prototype default.
- Pause while hovered and restart afterward.
- Provide clickable dot controls with `aria-label`s.
- Respect `prefers-reduced-motion`: keep manual controls but do not start autoplay.
- Use opacity/transform transitions; do not add a carousel dependency for this prototype.

## Responsive behavior

Keep the first desktop viewport compact enough to show hero and the first program section. If the right-side visual is hidden at tablet/mobile widths, the hero remains usable; otherwise stack it below copy and re-check viewport height.

## Verification

Fetch the cache-busted public artifact and assert:

- carousel container exists;
- expected slide count is present;
- autoplay code and reduced-motion guard exist;
- every slide contains a program-detail URL and real image URL;
- all linked detail routes and image URLs return HTTP 200;
- no `LINE_NUM|` prefixes or truncation markers were introduced;
- browser QA confirms rotation, dots, hover pause, keyboard links, and first-viewport composition.
