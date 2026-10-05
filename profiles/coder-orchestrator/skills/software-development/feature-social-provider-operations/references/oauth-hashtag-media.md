# OAuth, hashtags, media

OAuth state is random/hashed/user-bound/one-use; callback exact redirect; tokens server-only; DTO sanitized; disconnect revokes/clears. Enforce auth regardless of optional env. Hashtag quota counts distinct normalized tags/account in rolling provider window; top/recent cache TTL differs. Media parsers bound reads and handle malformed PNG/JPEG/WebP signatures and MP4 box lengths without panic. Publishing requires externally reachable provider-compatible media URLs.
