# Source access recipes

Working curl commands. All assume a normal browser UA for the human-facing sites.

## Wikipedia (no UA needed, JSON API)

```bash
# one-paragraph summary + canonical URL + thumbnail
curl -s "https://en.wikipedia.org/api/rest_v1/page/summary/Climate_change_in_the_Middle_East_and_North_Africa"

# full plaintext (best for bulk reading — no HTML stripping required)
curl -s "https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1&format=json&titles=<Title>" -o /tmp/a.json
python3 -c "import json;d=json.load(open('/tmp/a.json'));print(list(d['query']['pages'].values())[0]['extract'])"

# find the right title first when you're not sure of exact naming
curl -s "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=Middle+East+heat+record&format=json&srlimit=8"
```

Notes:
- `rest_v1/page/summary/<wrong-title>` → HTTP 404 with an empty-ish body, no suggestions. `action=query&titles=` instead returns `{"missing": ""}` **and** a `normalized` block telling you the correct title.
- The `extracts` API is far cheaper than scraping the rendered page — use it whenever you just need to read.

## DuckDuckGo

```bash
# WORKS — lite endpoint, no CAPTCHA
curl -sL "https://lite.duckduckgo.com/lite/?q=<url+encoded+query>" -A "Mozilla/5.0 (X11; Linux x86_64)" \
  | grep -oE 'uddg=[^&"]*' | head -6    # gives percent-encoded target URLs

# ALSO WORKS — the HTML endpoint sometimes, but frequently serves a duck-CAPTCHA:
#   https://html.duckduckgo.com/html/?q=...
# If you see "Select all squares containing a duck", switch to lite.
```

Decode results with `python3 -c "import urllib.parse,sys;print(urllib.parse.unquote(sys.stdin.read()))"` or just eyeball — the hostnames are readable.

## Google News RSS (current events, no API key)

```bash
curl -sL "https://news.google.com/rss/search?q=<terms>&hl=en-US&gl=US&ceid=US:en" -A "Mozilla/5.0" \
  | grep -o '<title>[^<]*</title>' | head -12
```

- Headlines only — good for triage and for discovering which institution published something.
- Article `guid`/`link` values are opaque `news.google.com/rss/articles/CBMi...` redirects; they do not resolve cleanly with curl. Treat RSS as a **discovery index**, then search the story title on DDG lite to get the real URL, or go straight to the publisher's own newsroom.

## Institutional newsrooms (numbers you can cite)

These return clean server-rendered HTML that the generic extractor handles well:

- `https://public.wmo.int/news/media-centre/<slug>` — WMO press releases. Carry the headline stat + baseline + scenario in the lede.
- `https://www.worldbank.org/en/news/press-release/<yyyy>/<mm>/<dd>/<slug>`
- `https://www.worldbank.org/en/brief/<yyyy>/<mm>/<dd>/<slug>` — overview pages, good for program/finance figures.
- IPCC chapter PDFs — heavy; prefer the SPM via the WG site or quote from a secondary that cites it verbatim.

## Generic HTML → text extractor (stdlib only)

Works on ~any CMS page. Drops nav/footer noise by keeping only long lines.

```python
import re, html
t = open(path, encoding='utf-8', errors='ignore').read()
t = re.sub(r'(?s)<script.*?</script>|<style.*?</style>', '', t)
t = re.sub(r'(?s)<[^>]+>', '\n', t)
t = html.unescape(t)
lines = [l.strip() for l in t.split('\n') if len(l.strip()) > 60]
print('\n'.join(lines)[:5000])
```

Tune the 60-char threshold: news sites need ~60–80, institution pages ~70. Lower it and you get menu items; raise it and you drop short paragraphs.

## Known-fragile endpoints

| Site | Behaviour | Workaround |
|---|---|---|
| `html.duckduckgo.com` | Duck CAPTCHA on datacenter IPs | use `lite.duckduckgo.com/lite/` |
| `insideclimatenews.org` | 403 to curl | find the same story on another outlet |
| `argusmedia.com` | 202 + JS shell, empty body | ditto |
| `worldbank.org` public API (`climateknowledgeportal`) | 403 on the download endpoint | read the press release / brief page instead |
| Google News article links | opaque redirect, no Location | search the headline text again |

The pattern for all of these: **never fight a blocked page — find a mirror of the same story.** Institutional press releases and Wikipedia cite the same underlying report, which is what you actually want to quote anyway.
