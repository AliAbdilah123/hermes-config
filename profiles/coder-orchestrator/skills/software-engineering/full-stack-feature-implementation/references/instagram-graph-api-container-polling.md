# Instagram Graph API Container Polling (Go)

## Context

When publishing images to Instagram via the Content Publishing API (2-step container flow), the media container needs time to process on Instagram's servers before it can be published. Calling `media_publish` immediately after container creation fails with:

```
Instagram media publish failed: status 400:
{"error":{"code":9007,"error_subcode":2207027,"message":"Media ID is not available",
 "error_user_msg":"Media belum siap untuk menerbitkan, tunggu beberapa saat lagi"}}
```

The fix is to poll the container status endpoint until it reaches `FINISHED`.

## Two-step Instagram publish flow

1. **Create container** — `POST /{ig-user-id}/media` with `image_url` + `caption`
2. **Poll container status** — `GET /{container-id}?fields=status_code` until `FINISHED`
3. **Publish** — `POST /{ig-user-id}/media_publish` with `creation_id`

## Container status codes

| Code | Meaning |
|------|---------|
| `FINISHED` | Ready to publish |
| `IN_PROGRESS` | Still processing — retry |
| `ERROR` | Permanent failure |
| `EXPIRED` | Container expired before publish |
| `PUBLISHED` | Already published |

## Go polling implementation

```go
func waitForInstagramContainer(client *http.Client, graphVersion, igUserID, token, containerID string, timeout time.Duration) error {
    deadline := time.Now().Add(timeout)
    delay := 1 * time.Second
    for {
        if time.Now().After(deadline) {
            return fmt.Errorf("Instagram media container not ready after %v", timeout)
        }
        statusURL := fmt.Sprintf("https://graph.instagram.com/%s/%s?fields=status_code&access_token=%s",
            graphVersion, containerID, url.QueryEscape(token))
        res, err := client.Get(statusURL)
        if err != nil {
            time.Sleep(delay)
            delay = time.Duration(float64(delay) * 1.5)
            if delay > 5*time.Second { delay = 5 * time.Second }
            continue
        }
        body, _ := io.ReadAll(io.LimitReader(res.Body, 64<<10))
        res.Body.Close()

        var out struct{ StatusCode string `json:"status_code"` }
        if json.Unmarshal(body, &out) != nil {
            time.Sleep(delay)
            delay = time.Duration(float64(delay) * 1.5)
            if delay > 5*time.Second { delay = 5 * time.Second }
            continue
        }
        switch out.StatusCode {
        case "FINISHED":
            return nil
        case "ERROR", "EXPIRED":
            return fmt.Errorf("Instagram container %s: status=%s", containerID, out.StatusCode)
        default: // IN_PROGRESS or empty
            time.Sleep(delay)
            delay = time.Duration(float64(delay) * 1.5)
            if delay > 5*time.Second { delay = 5 * time.Second }
        }
    }
}
```

## Usage in publish flow

```go
containerID, err := createInstagramMediaContainer(client, graphVersion, igUserID, token, imageURL, caption)
if err != nil {
    return PublishResult{OK: false, Error: err.Error()}
}
if err := waitForInstagramContainer(client, graphVersion, igUserID, token, containerID, 20*time.Second); err != nil {
    return PublishResult{OK: false, Error: err.Error()}
}
mediaID, err := publishInstagramMediaContainer(client, graphVersion, igUserID, token, containerID)
```

## Pitfalls

- **Don't skip polling**: Container processing typically takes 1–5 seconds but can take longer. A 20s timeout with exponential backoff (1s→5s max) is conservative enough.
- **Handle ERROR/EXPIRED as permanent failure**: Don't retry these — report them so the user knows.
- **Network errors are retryable**: If the status check fails with a network error, keep polling — the container may still be processing.
