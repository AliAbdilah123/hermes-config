# Profile avatar crop reuse

When adding crop-before-upload for SocialZen profile photos:

- The avatar upload flow is in `apps/frontend/src/pages/settings/SettingsPage.tsx` (`ProfileTab`, `handleAvatarUpload`).
- Reuse the existing frontend `PhotoCropModal` instead of adding a crop dependency.
- Keep avatar cropping square (`1:1`) by default because the visible avatar UI is round/square in Settings, Topbar, and Sidebar.
- Validate the selected file before opening the cropper: JPEG/PNG/WebP and the existing max-size rule.
- Store the selected file as pending state; Cancel/X must clear pending state and must not upload the original file.
- Apply should create/upload the cropped file via existing `uploadAvatar(apiUrl, file)`, then call `authClient.refreshSession()` so Topbar/Sidebar update immediately.
- Verify with frontend typecheck/build, deploy to `/var/www/html/projects/socialzen/`, grep deployed bundle for the crop-profile marker/copy, then public app link check.

Keep this as a small Settings-page integration unless profile image requirements change; do not introduce a backend image service unless browser canvas crop becomes insufficient.
