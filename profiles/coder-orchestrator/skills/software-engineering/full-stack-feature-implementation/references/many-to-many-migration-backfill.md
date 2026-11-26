# Many-to-many migration: backfill or you orphan existing rows

When a scalar foreign-key relation becomes many-to-many (e.g. a post owned by one
guild → a post shared to many guilds), you add a junction table and change the
queries to join through it. **That alone silently deletes existing data from every
read path**: old rows have no junction entries, so `JOIN junction` returns nothing
for them and the feed/counts suddenly look empty after deploy.

## The fix

Add an idempotent backfill step that runs on every open/migrate, right after the
junction table's `CREATE TABLE IF NOT EXISTS`. Insert one junction row per existing
parent, sourced from the old scalar column, skipping parents that already have one.

```go
// db.go — runs at startup, after the junction DDL.
func ensurePostGuilds(db *sql.DB) error {
    // INSERT only where a junction row is missing, so repeat runs are no-ops
    // and new parents created later are unaffected.
    _, err := db.Exec(`
        INSERT INTO post_guilds (post_id, guild_id)
        SELECT id, group_id FROM posts
        WHERE NOT EXISTS (
            SELECT 1 FROM post_guilds pg WHERE pg.post_id = posts.id
        )`)
    return err
}
```

Call it inside the same migration block that creates the junction indexes. Pin it to
`WHERE NOT EXISTS` (not `INSERT OR IGNORE` alone) so re-running never duplicates and
a post deliberately shared to zero guilds later is still respected.

## Verify after deploy, don't assume

The migration is invisible on a green build. Against the **live** DB, assert the
counts match after restart:

```bash
sqlite3 data/app.db "SELECT COUNT(*) FROM posts; SELECT COUNT(*) FROM post_guilds;"
```

For a revision that changes `posts.group_id` → `post_guilds`, the two counts should
equal (every legacy post got one junction row). If they don't, the backfill didn't run
or the WHERE clause is too narrow.

## Semantics to decide at the same time

- **Origin vs. current guild**: keep the old scalar as the parent's *origin* field
  (e.g. `Post.groupId`) for cross-guild display, and let the junction be what makes the
  row *visible* somewhere. Don't drop the scalar if the UI still shows "posted in X".
- **Delete scope**: deleting a shared parent now removes it everywhere (all junction
  rows), not just from the guild that issued the delete. Call this out in the API docs
  and in the delete confirmation copy.
- **Authorization**: any `WHERE posts.group_id = $guild` predicate that was doing
  visibility or ownership must move to a `JOIN post_guilds ON post_id = posts.id AND
  guild_id = $guild`. Miss one and the feature works in the list endpoint but 404s or
  leaks in like/comment/delete.

## Public E2E is the real regression signal

Existing tests still pass after this change *because the backfill preserves old
single-guild rows*. That is not proof the junction works — add at least one test that
shares a parent into a second guild and asserts it appears in both guilds and only
their members' feed, then run the project's public E2E suite against a live boot.