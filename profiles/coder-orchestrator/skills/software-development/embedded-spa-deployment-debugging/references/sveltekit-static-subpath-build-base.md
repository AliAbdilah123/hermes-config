# SvelteKit static SPA blank page under an Nginx subpath

## Symptom and diagnosis

Public HTML returns `200`, but the page is blank. Generated scripts/styles begin with `/_app/...` even though the app is mounted at a path such as `/projects/app/`. Root asset requests return `404`, while `/projects/app/_app/...` exists.

1. Fetch public HTML and extract all `.js`/`.css` `src` and `href` values.
2. Probe the emitted URL and expected mounted URL.
3. Read `svelte.config.js`. A configurable setting such as `paths: { base: process.env.BASE_PATH ?? '' }` works only when the deployment build exports `BASE_PATH`.
4. Inspect `build/index.html`; source configuration alone is not deployment evidence.

The durable distinction is **source defect versus invocation defect**. If base-path support and its regression test already exist, do not edit source or manufacture a commit. Rebuild with:

```bash
BASE_PATH=/projects/app npm run build
```

Then republish the complete clean `build/` directory. Never hand-edit generated HTML or copy only `index.html`; hashed assets must stay consistent.

## Verification

Before publishing:

```python
from pathlib import Path
s = Path('build/index.html').read_text()
assert '/projects/app/_app/' in s
assert 'href="/_app/' not in s
assert 'src="/_app/' not in s
```

After publishing:

- Fetch cache-busted public HTML.
- Require every emitted JS/CSS URL to start with the mount prefix.
- Probe every emitted asset for `200`, correct JS/CSS MIME type, and a non-empty body.
- Render the exact public URL in Chromium and require visible, non-blank UI. Separate host D-Bus/GPU warnings from page failures such as `Uncaught` or `net::ERR`.
- If the existing fix is committed, confirm that exact commit is contained by the tracked remote and report it as already pushed rather than creating a no-op commit.
