# VITE_ env vars in vitest: import.meta.env is NOT runtime-mutable

When a Vite/Vitest frontend reads `import.meta.env.VITE_SOME_KEY`, vitest's
Vite plugin inlines the value at transform time. This means:

## What does NOT work

1. **`vi.stubEnv('VITE_SOME_KEY', 'value')`** — modifies `process.env` only;
   `import.meta.env` was already inlined at module load and ignores it.

2. **Vitest config `env` option** — also sets `process.env`, same problem.

3. **Setting `process.env.VITE_SOME_KEY` in a setup file** — too late; the
   module was already transformed.

## What DOES work

**Shell env var at test-run time** (Vite picks it up during transform):

```bash
VITE_USD_TO_IDR_RATE=16000 npx vitest run src/__tests__/pricing.test.ts
```

This works because `import.meta.env.VITE_*` values are resolved from
`process.env` at Vite transform time, which runs before test execution.

## Alternative: mock the function that reads the env

If you can't control the shell env (CI, shared config), mock the function
that wraps the env read instead of trying to stub the env itself:

```ts
vi.mock('../lib/pricing', async () => {
  const actual = await vi.importActual('../lib/pricing')
  return { ...actual, getUsdToIdrRate: vi.fn(() => 16000) }
})
```

But prefer shell env — it's simpler and tests the real code path.

## When you need process.env fallback (for browser code)

If the utility needs to work in both Vite build (inlined) and test (shell env),
a `process.env` fallback seems natural but causes TypeScript errors in browser
targets (`Cannot find name 'process'`). Avoid it — keep the utility
browser-only (`import.meta.env`) and pass the env var to vitest via shell.

## Related: safe .env extraction for Vite builds

When building with a `VITE_*` var from a project's `.env`, extract just the
key to avoid sourcing the file (which leaks secrets into shell history):

```bash
RATE=$(python3 - <<'PY'
from pathlib import Path
for line in Path('.env').read_text().splitlines():
    if line.startswith('USD_TO_IDR_RATE='):
        print(line.split('=',1)[1].strip().strip('"').strip("'"))
        break
PY
)
cd apps/web && VITE_USD_TO_IDR_RATE="$RATE" npm run build
```

Never `set -a && . .env && set +a` — it dumps all secrets into the
shell environment visible to every child process.
