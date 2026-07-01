# External design fidelity: wallet pockets and layered metaphors

Use this note when adapting an external visual design (Google Stitch/Figma/exported HTML) into an existing app design system.

## Lesson

When a design contains a visual metaphor with layered geometry (for example a wallet pocket with voucher cards inside), preserving the **structure** matters more than token matching. A token-correct mockup can still be unacceptable if it changes the metaphor.

## Failure pattern to avoid

- Taking the user's requested design and mapping only fonts/colors into existing tokens.
- Compressing large card-like vouchers into skinny strips because they fit the existing page layout.
- Showing a review artifact that is technically responsive but visually far from the provided source.

In the Komuna wallet redesign, the user rejected the first artifact because voucher cards looked like "sticks" peeking from pockets. The corrected artifact worked after restoring the source design's structure:

- Tall wallet pocket cards.
- Full voucher cards stacked behind the pocket, not strips.
- Large angled flap covering the lower half.
- Dashed/stitch border on the flap.
- Modal vouchers styled as perforated ticket cards.
- A direct rejected-vs-approved comparison in the review artifact.

## Required workflow when adapting visual metaphors

1. Identify non-negotiable structural features in the source design before mapping tokens.
2. Preserve those features in the review artifact even when adapting colors/fonts to the existing site.
3. If simplifying, simplify only after checking whether the simplification changes the metaphor.
4. For review artifacts, include a high-fidelity component mockup of the key visual object, not just a conceptual approximation.
5. If the user rejects fidelity, revise the artifact first; do not implement from the rejected version.
6. When corrected, add a small visual comparison of "rejected direction" vs "approved target" if it helps lock the lesson.

## Quick checklist

- Does the adapted mockup preserve source object proportions?
- Are layered elements the same kind of object as the source (card vs strip, panel vs list row)?
- Does hover/interaction reinforce the same metaphor?
- Does mobile still show the intended object, not a collapsed-looking remnant?
- Would the user recognize the source design from the artifact without explanation?
