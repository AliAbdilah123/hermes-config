# Fresh final gate and Fetch response tests

## Final evidence

Any code or test edit makes earlier test, lint, typecheck, and build output stale. After the last modification, run one canonical chained gate covering every check requested by the user. Report only the final run, including its exact warning count and generated artifact names. A focused test passing does not compensate for a failing canonical suite.

Example:

```sh
npm test && npm run test:backend && npm run lint && npm run typecheck && npm run build
```

## Fetch/Undici response bodies are single-use

When a test needs response JSON both for diagnostics and assertions, parse it once:

```js
const body = await response.json();
assert.equal(response.status, 201, JSON.stringify(body));
const created = body.user;
```

Do not use `await response.text()` as an assertion message and then call `response.json()`. The first call consumes the stream, so the second throws `Body is unusable` and hides the actual behavior being tested.
