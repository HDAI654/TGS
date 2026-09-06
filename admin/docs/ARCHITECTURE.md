# Admin Architecture

The Admin service owns the shared PostgreSQL data and provides the Django Admin UI, monitoring pages, Celery worker, and Celery Beat schedule control.

It has no public business API. Its HTTP views are authenticated administrative pages.
