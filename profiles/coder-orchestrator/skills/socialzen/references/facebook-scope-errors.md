# Facebook Publishing Error Logs

## pages_manage_posts — Invalid Scope (OAuth)

When `pages_manage_posts` is included in `facebookScopes`, Meta rejects the OAuth dialog:

```
This content isn't available at the moment
Invalid Scopes: pages_manage_posts. This message is only shown to developers.
Users of your app will ignore these permissions if present.
```

Root cause: `pages_manage_posts` requires a **Business-type** Facebook app with Advanced Access.
A regular Facebook Login app cannot request this scope.

## pages_manage_posts — Publishing API Error

When attempting to POST to `/{page-id}/feed` without `pages_manage_posts`:

```
Facebook API error 403: {
  "error": {
    "message": "(#200) If posting to a page,
      requires both pages_read_engagement and pages_manage_posts as an admin with
      sufficient administrative permission",
    "type": "OAuthException",
    "code": 200
  }
}
```

This error means the page access token was obtained without `pages_manage_posts`.
Even if the user IS a page admin, the token lacks the required permission.

## Current Resolution

Facebook publishing is blocked until the app is upgraded to Business type.
The scopes in use are: `pages_show_list`, `pages_read_engagement`, `business_management`.
These allow reading page data and listing pages, but NOT creating posts.
