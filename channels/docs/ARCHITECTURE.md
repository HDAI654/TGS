# Channels Architecture

Channels is a public read-only FastAPI service. Its domain contains immutable dataclasses, its application layer contains query use cases, and its infrastructure layer contains SQLAlchemy read repositories.

The service has SELECT-only PostgreSQL credentials. There are no write repositories, mutations, unit-of-work abstractions, or authentication dependencies.
