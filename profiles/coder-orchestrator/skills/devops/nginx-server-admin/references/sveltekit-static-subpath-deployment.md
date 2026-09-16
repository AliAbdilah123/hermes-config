# SvelteKit static SPA deployment under an nginx subpath

Use when a client-only SvelteKit prototype must live at `/projects/<slug>/` without a long-running Node server.

## Source adaptation

1. Replace `@sveltejs/adapter-auto` with `@sveltejs/adapter-static`.
2. Put adapter and path configuration in `svelte.config.js`:

```js
import adapter from '@sveltejs/adapter-static';

export default {
  kit: {
    adapter: adapter({ fallback: 'index.html' }),
    paths: { base: process.env.BASE_PATH ?? '' }
  }
};
```

3. For a client-only prototype, export `ssr = false` from `src/routes/+layout.ts`.
4. Replace root-absolute internal navigation with SvelteKit path resolution:

```ts
import { resolve } from '$app/paths';
import { goto } from '$app/navigation';

resolve('/notes');
goto(resolve('/notes/new'));
```

This keeps local development at `/` while making a prefixed build safe. Do not manually prepend the base in every component.

5. Client-only fallback HTML may request `/favicon.ico` before hydration when the favicon exists only in `<svelte:head>`. Put the icon in `static/favicon.svg` and declare it in `src/app.html`:

```html
<link rel="icon" href="%sveltekit.assets%/favicon.svg" />
```

## Build and artifact checks

```bash
rm -rf build
BASE_PATH=/projects/<slug> npm run build
```

Require:
- `build/index.html` exists;
- emitted JS/CSS URLs begin with `/projects/<slug>/_app/`;
- no root-absolute internal links remain in Svelte source;
- `npm test` and `npm run check` pass.

## Nginx route

Insert this before the generic `/projects/` location:

```nginx
location = /projects/<slug> {
    return 301 https://<public-host>/projects/<slug>/;
}
location /projects/<slug>/ {
    alias /var/www/html/projects/<slug>/;
    index index.html;
    try_files $uri $uri/ /projects/<slug>/index.html;
}
```

Preserve literal `$uri` when generating config. Validate with `nginx -t` before reload. Deploy only to the leaf:

```bash
sudo rsync -a --delete build/ /var/www/html/projects/<slug>/
```

Never target the shared `/var/www/html/projects/` parent with `--delete`.

## Public verification

1. Confirm no-slash URL redirects to public HTTPS.
2. Confirm root and real deep routes return the deployment's fallback HTML.
3. Extract emitted JS/CSS URLs from public HTML and require correct MIME types.
4. Check the prefixed favicon returns `image/svg+xml`.
5. Run Chromium against the exact public URL: login/navigation, one state-changing flow, deep route, console/page errors, failed responses, and 320/375/414/768 widths.
6. When a console resource error has no obvious response record, log the console event location. Chromium may reveal a host-root `/favicon.ico` request; fix the static head declaration rather than suppressing the error or modifying a shared host favicon.

## Git/deploy ordering

Push the verified source adaptation first, deploy that exact commit's build second, then verify remote `main`, local clean status, and the public artifact. Report the public URL and exact commit only after browser E2E passes.
