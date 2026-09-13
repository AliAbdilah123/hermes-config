# Nested SPA preview entry contract

Use this when a SPA preview is mounted below a path such as `/previews/<slug>/`.

## Pre-browser gate

1. Build with the preview's exact public base, or with `base: './'` when the artifact must be path-portable.
2. Fetch the public entry HTML and inspect the emitted JS/CSS URLs. HTTP 200 on the entry document is insufficient.
3. Probe each entry asset at the URL the browser will resolve and require the correct MIME type.
4. If client requests are root-relative (`/api/...`), inject a preview API-base value and make the client consume it.
5. Confirm the injection marker is present in the served HTML. Do not assume an nginx `sub_filter` matched; minimal generated HTML may not contain the token (such as `</head>`) that the filter targets.
6. Only then launch browser E2E. If the first expected UI control never appears, inspect entry assets, API-base injection, DOM, and console before weakening locators.

## Single-option settings contract

A visible option label is not necessarily the persisted identifier. Give options explicit values even when the control is disabled or currently has one provider:

```html
<select value="hermes" disabled>
  <option value="hermes">Hermes</option>
</select>
```

Browser E2E should compare the DOM value to the API/database identifier. This catches settings UIs that display the right label but submit a different value.

## Verification summary

Require all of these independently:

- entry HTML 200;
- emitted JS/CSS URL and MIME checks;
- preview API returns JSON rather than SPA HTML;
- runtime API-base marker is present;
- browser renders the first expected control;
- exact interaction and persistence flow passes;
- console/page errors are clean.
