# Frontend auth UX gates

Use this when implementing the frontend slice of SocialZen auth verification/reset UX.

## Compact pattern

- Signup: after `authClient.signUp.email(...)`, call `authClient.refreshSession()`. If `session.user.emailVerified === false`, show an inline check-email state instead of navigating straight to paid plan/app flow. Let the user continue to the dashboard, but make it clear publishing and social connects stay locked until verification.
- Login: when email sign-in returns `PASSWORD_NOT_SET`, show explicit copy that the account uses Google Sign-In and can add/reset a SocialZen password. Because the login code races the auth call against a timeout promise, narrow with `"code" in error` before reading `error.code`.
- Restricted actions: map `EMAIL_NOT_VERIFIED` to user-safe copy anywhere the backend already gates the action, especially Create Post submit and social OAuth start helpers.
- API errors: prefer `ApiError.code` from `lib/api.ts`; do not dig into `err.body.error.code` unless that endpoint actually nests errors. The auth/API helpers generally expose the top-level `code` already.

## Verification

```bash
cd /home/ubuntu/socialzen/apps/frontend
pnpm typecheck
pnpm build
sudo rsync -a --delete dist/ /var/www/html/projects/socialzen/
sudo chown -R www-data:www-data /var/www/html/projects/socialzen
curl -sI http://localhost/projects/socialzen/ | head -1
curl -sI "https://socialzen.ahsanworks.com/projects/socialzen/assets/<new chunk>.js" | grep -i content-type
```

After deploy, grep the deployed chunks for distinctive copy such as `Verify before`, `PASSWORD_NOT_SET` guidance, or `EMAIL_NOT_VERIFIED` to prove production has the new bundle.
