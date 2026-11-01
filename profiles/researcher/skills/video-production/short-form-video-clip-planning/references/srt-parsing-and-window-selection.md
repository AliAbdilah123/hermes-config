# SRT parsing + clip-window selection recipe

Working script from a 4,300-line / 92-minute lecture SRT. Two phases: parse
cues once, then search for valid windows instead of reading the transcript
linearly.

## Phase 1 — parse cues, drop junk

Generated SRTs from auto-caption pipelines contain three kinds of garbage that
must be discarded **before** selecting clips:

1. `00:01:56,069 --> NaN:NaN:NaN,NaN` — broken end timestamp. Skip the record.
2. Empty text blocks (blank line between the two timestamps).
3. Cue numbers that are not contiguous (the file jumps 1,2,3… but the parser
   must key off the real integer, not the position).

```python
import re

def load_cues(path):
    s = open(path, encoding='utf-8').read().replace('\r', '')
    cues = []
    for block in re.split(r'\n\s*\n', s):
        m = re.match(r'(\d+)\n([^\n]+) --> ([^\n]+)\n(.*)', block, re.S)
        if not m or 'NaN' in m.group(2) + m.group(3):
            continue
        text = ' '.join(m.group(4).split())   # join multi-line cues, collapse spaces
        if not text:
            continue
        cues.append((int(m.group(1)), m.group(2), m.group(3), text))
    return cues

def sec(t):                     # '01:04:59,520' -> float seconds
    h, m, x = t.replace(',', '.').split(':')
    return int(h) * 3600 + int(m) * 60 + float(x)

def mmss(t):                    # '01:04:59,520' -> '1:04:59'  ('04:59' under an hour)
    h, m, x = t.split(':')
    q = f'{int(m):02d}:{int(float(x.replace(",", "."))):02d}'
    return q if int(h) == 0 else f'{int(h)}:{q}'
```

Keep the original millisecond string around for the duration/overlap checks and
convert only at serialization — truncating early makes two adjacent cues look
identical and hides off-by-a-frame errors.

## Phase 2 — survey before reading

Do not read 90 minutes of transcript linearly. Sample every 5 minutes to learn
the structure (intro / demo / Q&A / closing), then zoom into the promising
bands.

```python
for minute in range(5, 91, 5):
    i = min(range(len(cues)), key=lambda j: abs(sec(cues[j][1]) - minute * 60))
    print(' '.join(f'[{c[0]} {c[1][:8]}] {c[3]}' for c in cues[i:i + 18]))
```

Then, per target region, enumerate *candidate windows* that already satisfy the
duration and sentence-boundary rules, instead of hand-picking cue ranges and
discovering later that they are 28 s or end mid-clause:

```python
for i, c in enumerate(cues):
    if not (target_start <= sec(c[1]) <= target_start + 20):
        continue
    if not (c[3][0].isupper() or c[3].startswith(('Nah', 'Ee', 'Jadi', 'Oke'))):
        continue                                  # plausible sentence start
    for j in range(i, len(cues)):
        d = sec(cues[j][2]) - sec(c[1])
        if 35 <= d <= 65 and cues[j][3].rstrip().endswith(('.', '?', '!')):
            print(c[0], cues[j][0], round(d, 1), c[3], '... END:', cues[j][3])
            break
```

This surfaces 3–6 viable windows per region in one pass. Pick from those; then
re-verify the final set with `assert` (duration range, contiguity, no overlap)
before writing JSON.

## Phase 3 — generate the artifact, don't hand-write it

Build the clip JSON in the same script from the chosen `(first_cue, last_cue)`
pairs, with `assert`s inline:

```python
assert 30 <= sec(z[-1][1]) - sec(z[0][0]) <= 75
assert sec(z[0][0]) >= prev_end          # no overlap with previous clip
```

Hand-transcribing 25 subtitle objects per clip is where verbatim-text and
timestamp errors come from; emitting them from the parsed cues makes both
classes of error impossible.

## Downstream note

The same script's output feeds a Remotion render. Emit `start`/`end` as
`MM:SS`/`H:MM:SS` per the request, but keep an internal seconds-based `data.ts`
(or equivalent) so the composition does not re-parse strings per frame.
