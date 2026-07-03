# Instagram Insights API

For reach, impressions, and saves (bookmarks), use the Instagram Insights endpoint:

```
GET https://graph.instagram.com/{version}/{media-id}/insights
    ?metric=reach,impressions,saved
    &period=lifetime
    &access_token={token}
```

## Response shape

```json
{
  "data": [
    {"name": "reach", "period": "lifetime", "values": [{"value": 1234}]},
    {"name": "impressions", "period": "lifetime", "values": [{"value": 5678}]},
    {"name": "saved", "period": "lifetime", "values": [{"value": 42}]}
  ]
}
```

## Gotchas

- **Not available for all posts**: New posts may not have insights yet. Handle `graphGet` errors gracefully — return nil instead of failing the sync.
- **Business/creator account required**: Insights only work for Instagram Business or Creator accounts, not personal accounts.
- **Token scope**: Requires the same `instagram_business_basic` scope used for media publishing. No additional scope needed.
- **`saved` metric name**: Instagram uses `saved` (not `saves`) as the metric key. Map it to the local DB column accordingly.

## Go extraction pattern

```go
metrics := map[string]int{}
for _, d := range insightResp.Data {
    if len(d.Values) > 0 {
        metrics[d.Name] = d.Values[0].Value
    }
}
app.DB.Exec(`UPDATE posts SET reach=?, impressions=?, saves=?, updated_at=? WHERE id=?`,
    metrics["reach"], metrics["impressions"], metrics["saved"], now, postID)
```

Always defensively use map lookup — missing keys silently default to 0 in Go, which is safe.
