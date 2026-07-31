# Conversational localization refinement

Use this pattern when feedback says a locale sounds rigid, official, or machine-translated.

## Editing contract

- Treat the locale catalog as one voice system, not a single-string substitution. Search the complete locale file for the rejected term, formal pronouns, and nearby stiff constructions.
- For casual-polite Indonesian, avoid `Anda`; use `kamu` only when a pronoun improves clarity, otherwise omit it.
- Prefer direct active phrasing and familiar product language over document-style passive constructions.
- Use conversational particles (`ya`, `nih`, `sih`) sparingly and only where a real speaker would naturally use them. Repeating particles across controls and status messages feels artificial.
- When the user rejects a lexical choice, update its user-facing variants consistently. Example: prefer `Cari` over rigid discovery copy built around `Temukan`, while preserving distinct actions such as browsing or filtering where `Jelajahi` or another verb is semantically better.
- Preserve established domain terminology exactly (for Komuna: `Simple product`). Do not introduce a translated synonym merely to make the locale uniformly Indonesian.

## Safety checks

1. Preserve every translation key, interpolation token (`{{count}}`, `{{name}}`), plural suffix, markup tag, and escape sequence.
2. Validate JSON after editing.
3. Mechanically assert rejected pronouns/terms are absent where the requested rule is global, and that required replacement wording is present.
4. Render representative surfaces rather than approving source text alone: discovery/landing, navigation, empty/error states, settings, and at least one transactional flow.
5. For a settings preview, authenticate on the exact public route, switch to the locale, reload, and confirm persistence. If locale and currency are independent, also verify both cross-combinations and that changing language does not alter currency.

## Pitfalls

- Blind global replacement that turns semantically distinct actions into the same verb.
- Replacing `Anda` with `kamu` in every sentence instead of rewriting naturally.
- Adding `nih/sih/ya` to many UI labels, making the interface sound performative.
- Editing only the headline named in feedback while the rest of the locale retains the rejected voice.
- Translating protected product terms or changing interpolation tokens.
