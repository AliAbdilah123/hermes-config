# Nginx proxy map after 2026-06-26 migration

Added to `/etc/nginx/projects/default.conf` inside the existing `server` block:

```nginx
location ^~ /projects/fnb-pos/api/v1/ {
    proxy_pass http://127.0.0.1:8080/api/v1/;
    ...
}

location ^~ /projects/local-business-os-indonesia/api/v1/ {
    proxy_pass http://127.0.0.1:8090/api/v1/;
    ...
}

location ^~ /projects/local-business-os-indonesia/healthz {
    proxy_pass http://127.0.0.1:8090/healthz;
    ...
}

location ^~ /projects/insta-scheduler/api/v1/ {
    proxy_pass http://127.0.0.1:8083/api/v1/;
    ...
}

location ^~ /projects/siapjasa/api/v1/ {
    proxy_pass http://127.0.0.1:8094/api/v1/;
    ...
}

location ^~ /projects/Komuna/api/v1/ {
    proxy_pass http://127.0.0.1:8091/api/v1/;
    ...
}
```

Note: `/projects/brand-organizer/api/` and `/projects/socialzen/api/` blocks already existed in this host's config prior to migration.
