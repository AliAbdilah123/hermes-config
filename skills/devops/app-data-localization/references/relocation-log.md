# Relocation Log (2026-06-26)

## Source → Destination pairs

| Source | Destination | Sidecar files |
|---|---|---|
| /var/lib/multitenant-auth-saas-boilerplate/app.db | /home/ubuntu/projects/multitenant-auth-saas-boilerplate/backend/data/app.db | none |
| /var/lib/brand-organizer/brand-organizer.db | /home/ubuntu/projects/brand-organizer/apps/backend-go/data/brand-organizer.db | none |
| /var/lib/local-business-os-indonesia/local-business-os.db | /home/ubuntu/projects/local-business-os-indonesia/data/local-business-os.db | none |
| /var/lib/siapjasa/siapjasa.db | /home/ubuntu/projects/siapjasa/data/siapjasa.db | scheduler.db-shm, scheduler.db-wal |
| /var/lib/socialzen/socialzen.db | /home/ubuntu/socialzen/data/socialzen.db | none |
| /var/lib/insta-scheduler/scheduler.db | /home/ubuntu/projects/insta-scheduler/backend/scheduler.db | scheduler.db-shm, scheduler.db-wal |
| /var/lib/komuna/komuna.db | /home/ubuntu/projects/Komuna/api/data/komuna.db | komuna.db-shm, komuna.db-wal |

## Env changes

- `/home/ubuntu/projects/brand-organizer/.env`: `DATABASE_PATH=/var/lib/brand-organizer/brand-organizer.db` → `/home/ubuntu/projects/brand-organizer/apps/backend-go/data/brand-organizer.db`
- `/home/ubuntu/projects/multitenant-auth-saas-boilerplate/.env`: appended `DATABASE_PATH=/home/ubuntu/projects/multitenant-auth-saas-boilerplate/backend/data/app.db`
- `/home/ubuntu/socialzen/.env`: created with `DATABASE_PATH`; kept `MEDIA_DIR=/var/lib/socialzen/media`
- `/etc/komuna/komuna.env`: created with `KOMUNA_DB_PATH=/home/ubuntu/projects/Komuna/api/data/komuna.db`

## Gitignore additions

- `/home/ubuntu/projects/siapjasa/.gitignore`: added `data/`
- `/home/ubuntu/socialzen/.gitignore`: added `data/` and `*.db`

## Systemd unit changes

- multitenant-auth-saas.service: WorkingDirectory + DATABASE_PATH updated.
- brand-organizer.service: WorkingDirectory + DATABASE_PATH + ReadWritePaths updated.
- local-business-os-indonesia.service: DB_PATH updated.
- siapjasa.service: SIAPJASA_DATA_DIR updated.
- insta-scheduler.service: DB_FILE + ReadWritePaths updated.
- komuna-api.service: ReadWritePaths trimmed to project data dir only.

## Restart outcomes

- ✅ multitenant-auth-saas
- ✅ brand-organizer
- ✅ local-business-os-indonesia
- ✅ siapjasa
- ✅ insta-scheduler
- ❌ socialzen — port 8080 conflict (pre-existing)
- ❌ komuna-api — port 8080 conflict (pre-existing)
