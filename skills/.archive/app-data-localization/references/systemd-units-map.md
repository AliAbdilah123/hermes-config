# Systemd Units Map (observed 2026-06-26)

| Service | Unit file | Runtime user | WorkingDirectory | DB env var | DB path after relocation | Extra read/write paths |
|---|---|---|---|---|---|---|
| multitenant-auth-saas.service | /etc/systemd/system/multitenant-auth-saas.service | ubuntu | /home/ubuntu/projects/multitenant-auth-saas-boilerplate | DATABASE_PATH | /home/ubuntu/projects/multitenant-auth-saas-boilerplate/backend/data/app.db | — |
| brand-organizer.service | /etc/systemd/system/brand-organizer.service | www-data | /home/ubuntu/projects/brand-organizer | DATABASE_PATH (from .env) | /home/ubuntu/projects/brand-organizer/apps/backend-go/data/brand-organizer.db | /var/lib/brand-organizer/media (kept) |
| local-business-os-indonesia.service | /etc/systemd/system/local-business-os-indonesia.service | www-data | /var/lib/local-business-os-indonesia | DB_PATH | /home/ubuntu/projects/local-business-os-indonesia/data/local-business-os.db | — |
| siapjasa.service | /etc/systemd/system/siapjasa.service | root | — | SIAPJASA_DATA_DIR | /home/ubuntu/projects/siapjasa/data | — |
| socialzen.service | /etc/systemd/system/socialzen.service | (jailed) | /opt/socialzen | DATABASE_PATH (from .env) | /home/ubuntu/socialzen/data/socialzen.db | — |
| insta-scheduler.service | /etc/systemd/system/insta-scheduler.service | www-data | /opt/insta-scheduler | DB_FILE | /home/ubuntu/projects/insta-scheduler/backend/scheduler.db | backend dir only |
| komuna-api.service | /etc/systemd/system/komuna-api.service | ubuntu | /home/ubuntu/projects/Komuna/api | KOMUNA_DB_PATH (from /etc/komuna/komuna.env) | /home/ubuntu/projects/Komuna/api/data/komuna.db | — |

## Notes

- `socialzen` and `komuna-api` both default to **port 8080** in source. If another service (e.g. `fnb-pos.service`) already binds `:8080`, both will fail with `bind: address already in use`; this is not a DB issue.
- `brand-organizer` still stores media under `/var/lib/brand-organizer/media`; update `MEDIA_DIR` only if you also migrate the media tree.
- `komuna` originally referenced `/var/lib/komuna` in `ReadWritePaths`; after moving the DB, this line should be removed.
