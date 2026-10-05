# Lazy media cache

Owner opens detail -> load original reference -> if available serve cached bytes -> if another fresh claim exists omit enrichment -> otherwise conditional missing/failed/stale-claim to claiming -> fetch only allowlisted HTTPS hosts, rejecting unsafe redirects and bounding bytes/type -> atomically store then mark available. On failure mark failed while retaining original URL/ID; later opens may retry after cooldown.
