# Light POS compaction + idempotency patterns

Concrete TypeScript/Node patterns extracted from the offline-first fix in `light-pos`.

## Compaction instead of rebase

`rebaseOperation` (rewriting `baseRevision`) was the anti-pattern — it mutates an already-persisted immutable snapshot. Replace with compaction that keeps the stable `id` + original `baseRevision`, only swapping `action`/`data`, and refuses cross-scope merges:

```ts
export const compactOperation=<T>(operation,data,action,scope={userId:operation.userId,business:operation.business}) => {
  if(scope.userId!==operation.userId||scope.business!==operation.business) throw Error('Operation scope mismatch.');
  return {...operation,action,data};
};
```

Test it before implementing (RED): assert `compactOperation(first, latest, 'Second')` deep-equals `{...first, action:'Second', data:latest}`; assert a cross-user/tenant call throws `'scope'`.

## Atomic durable persistence

Outbox + snapshot must commit in ONE IndexedDB transaction so a quota/abort can't strand optimistic state:

```ts
export const persistLatest=async<T>(operation,snapshot)=>{
  const db=await open();
  await new Promise<void>((resolve,reject)=>{
    const tx=db.transaction(['snapshots','outbox'],'readwrite');
    tx.objectStore('outbox').put(operation);
    tx.objectStore('snapshots').put(snapshot,snapshotKey(snapshot.userId,snapshot.business));
    tx.oncomplete=()=>resolve(); tx.onerror=tx.onabort=()=>reject(tx.error);
  });
  db.close();
};
```

Queue chain must be recoverable: `queue.current = queue.current.catch(()=>undefined).then(async ()=>{...})`.

## Store `update()` — synchronous scope capture

Capture before the queue, never inside it:

```ts
const snapshot=structuredClone(next), id=++generation.current,
      user=sessionRef.current, target=businessRef.current, baseRevision=revision.current;
if(!user) return;
```

If `indexedDB` is undefined, do not pretend durability — surface it: `setSyncError('This change is not durable because browser storage is unavailable.')`.

## Server idempotency + lost-response reconciliation

Lookup by global `id` only; scope mismatch → 409; persist the accepted snapshot:

```js
const seen=db.prepare('SELECT actor_id,business_id,status,result_revision revision,result_data FROM sync_operations WHERE id=?').get(operation.id);
if(seen){
  if(seen.actor_id!==user.id||seen.business_id!==operation.business) return json(res,409,{error:'Operation ID belongs to another scope.'});
  results.push({status:seen.status,revision:seen.revision, ...(seen.result_data?{data:JSON.parse(seen.result_data)}:{})});
  continue;
}
// ... on commit:
db.prepare('INSERT INTO sync_operations(id,actor_id,business_id,status,created_at,result_revision,result_data) VALUES(?,?,?,?,?,?,?)')
  .run(operation.id,user.id,operation.business,'accepted',operation.createdAt,revision,JSON.stringify(data));
```

Existing DBs need a migration (the `result_data` column added after the table shipped):

```js
const syncColumns=db.prepare('PRAGMA table_info(sync_operations)').all();
if(!syncColumns.some(x=>x.name==='result_data')) db.exec('ALTER TABLE sync_operations ADD COLUMN result_data TEXT');
```

Client-side, when a sync result lacks `data`, fetch authoritative state before removing the op so the client can reconcile server-normalized data/audit after a lost response.

## Session-owner validation before replay

```ts
const owner=(await api('/session')).user as Session;
if(owner.id!==user.id) throw Object.assign(Error('Session owner changed.'),{status:403});
```

On 401/403: set a "Sign in as the owner of these offline changes to sync" message, keep pending ops, and do NOT purge the outbox.

## Build-versioned service worker (no new deps)

Generate `sw.js` at build time from a pure function + a script that parses the built `index.html`:

```js
// scripts/build-service-worker.mjs
import {createHash} from 'node:crypto';
const assets=[...html.matchAll(/(?:src|href)="[^"]*?\/assets\/([^"?]+)/g)].map(m=>`assets/${m[1]}`);
const unique=[...new Set(assets)].sort();
const version=`build-${createHash('sha1').update(base+unique.join('|')).digest('hex').slice(0,12)}`;
writeFileSync(join(outDir,'sw.js'), buildServiceWorker({base,version,assets:unique}));
```

The `build` script chains it: `tsc -b && vite build && node scripts/build-service-worker.mjs`.

**Gotcha:** importing a `.ts` module from a plain `.mjs` build script needs the explicit extension and a relative (`../`) path — `import {buildServiceWorker} from '../src/serviceWorker.ts'` — or Node resolves it against the script's own directory and throws `ERR_MODULE_NOT_FOUND` (`Cannot find module '.../scripts/src/serviceWorker'`).

**Gotcha:** the precache regex must match **absolute** asset URLs (`/projects/<app>/assets/...`) which is what Vite emits with a non-root `base`; a root-relative `/assets/...` regex yields zero assets.

The generated worker: versioned `CACHE` name, `install` does `cache.addAll(PRECACHE).then(()=>self.skipWaiting())`, `activate` deletes only keys with the app prefix (`key.startsWith(prefix) && key!==CACHE`) then `clients.claim()`, and `fetch` returns early for `url.pathname.startsWith(BASE+'api/')`.

## Test tricks

- Backend tests live outside vitest — run `npm run test:backend` (node --test) separately from `npm test`.
- When the test needs two authenticated scopes, both must be *different tenants-accessible identities* (e.g. `admin.harbor` and `manager.harbor`): reusing `cashier.harbor` as the second actor trips the `businessIds.includes('*')` superadmin guard and returns 403 before the idempotency branch.
- Idempotency tests must actually mutate: `validState` on the server's unchanged data returns `403 {error:"No changes supplied"}`, masking whether the idempotency lookup was reached.