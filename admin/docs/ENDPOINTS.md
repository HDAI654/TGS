# Admin Endpoints

The Admin service exposes no public business API. Its HTTP routes are authenticated Django Admin/custom monitoring views.

- `/admin/` — Django Admin.
- `/admin/monitoring/` — system dashboard.
- `/admin/monitoring/channels/` — Channels health.
- `/admin/monitoring/workers/` — Celery worker health.
- `/admin/monitoring/logs/` — recent application logs.
- `/admin/worker-control/` — worker interval configuration.
