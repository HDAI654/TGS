<!--
README.md – TGS International TV Streaming Platform
SEO Keywords: FastAPI, GraphQL, Strawberry, SQLAlchemy, TV streaming, live channels, video streaming platform, backend API, modern Python, async, scalable, open source.
-->

# 🌍 TGS – International TV Streaming Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Strawberry](https://img.shields.io/badge/Strawberry-0.259.0-FF6B6B?logo=strawberry)](https://strawberry.rocks)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.36-8B0000?logo=sqlalchemy)](https://www.sqlalchemy.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis)](https://redis.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> **TGS** (The Global Stream) is a modern, fast, and scalable backend for an international TV streaming platform.  
> Built with **FastAPI**, **SQLAlchemy**, and **Strawberry GraphQL**, it serves live channel data, country metadata, and video streams through a clean REST + GraphQL API.

---

## 🚀 Features

- ✅ **Authentication & Authorization** – JWT-based login, signup, password reset, and device‑bound sessions.
- ✅ **GraphQL API** – Query channels and countries with full CRUD operations (no over‑fetching).
- ✅ **REST Admin API** – Administrative endpoints for data synchronization (channels, countries, full sync).
- ✅ **Modular Clean Architecture** – Clean separation of domain, application, infrastructure, and presentation layers.
- ✅ **Device Binding** – Secure sessions tied to user devices to prevent token theft.
- ✅ **Celery Integration** – Asynchronous background tasks for syncing external data.
- ✅ **Comprehensive Testing** – Unit, integration, and end‑to‑end tests with `pytest`.
- ✅ **Production‑Ready** – Docker Compose setup with healthchecks, logging, and volume persistence.

---

## 🧰 Tech Stack

| Layer          | Technology                                                       |
|----------------|------------------------------------------------------------------|
| **Web Framework** | [FastAPI](https://fastapi.tiangolo.com) – high‑performance, async |
| **GraphQL**    | [Strawberry](https://strawberry.rocks) – modern GraphQL library   |
| **ORM**        | [SQLAlchemy](https://www.sqlalchemy.org) – async, with PostgreSQL |
| **Database**   | [PostgreSQL](https://www.postgresql.org) 15 + asyncpg            |
| **Cache / Session** | [Redis](https://redis.io) 7 (caching, session storage)        |
| **Task Queue** | [Celery](https://docs.celeryq.dev) with Redis as broker          |
| **Auth**       | JWT (RS256) with device fingerprinting                           |
| **Testing**    | `pytest`, `httpx`, `fakeredis`, `aiosqlite`                     |
| **Container**  | Docker & Docker Compose                                          |

---

## 📁 Project Structure

```
.
├── docker-compose.yml
├── Dockerfile
├── keys/                  # RSA keys for JWT
├── src/
│   ├── modules/
│   │   ├── auth/         # Authentication module (domain, app, infra, presentation)
│   │   ├── channels/     # Channels & Countries module (domain, app, infra, presentation)
│   │   └── core/         # Shared utilities, config, database, redis client
│   ├── logging_config.py
│   └── main.py
├── workers/              # Celery tasks and configuration
├── test/                 # Unit, integration, and e2e tests
├── logs/                 # Application logs
├── requirements.txt
├── run_tests.sh
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (optional, for local development)

### 1. Clone the repository

```bash
git clone https://github.com/HDAI654/TGS.git
cd tgs
```

### 2. Configure environment variables

Edit `docker-compose.yml` and set your values for:

- `SMTP_USER`, `SMTP_PASSWORD`, `FROM_EMAIL`
- `AUTH_TOKEN_PRIVATE_KEY` / `AUTH_TOKEN_PUBLIC_KEY` paths (keys are mounted from `./keys/`)
- and other ...

### 3. Build and run

```bash
docker compose up --build
```

This starts:
- `main-app` (FastAPI server on port 8000)
- `celery_worker` (Celery worker)
- `db` (PostgreSQL)
- `redis` (Redis)

### 4. Check health

```bash
docker compose ps
```

All services should show `healthy`.

---

## 🧪 Testing

### Run all tests

```bash
sh run_tests.sh
```

### Run specific test folders

```bash
sh run_tests.sh test/unit/auth/domain
sh run_tests.sh test/e2e
```

---

## 🔌 API Overview

### GraphQL Endpoint

`POST /graphql/v1` – Full CRUD for `Country` and `Channel` entities.

**Example: Create a country**

```graphql
mutation {
  createCountry(
    countryCode: "FR",
    countryName: "France",
    capital: "Paris",
    timezone: "Europe/Paris",
    channelCount: 8
  ) {
    countryCode
    countryName
  }
}
```

> See full examples in the [Usage section](#example-usage).

### REST Admin Endpoints

| Method | Endpoint                      | Description                |
|--------|-------------------------------|----------------------------|
| POST   | `/api/v1/admin/sync/all`      | Sync all data (channels + countries) |
| POST   | `/api/v1/admin/sync/channels` | Sync channels only         |
| POST   | `/api/v1/admin/sync/countries`| Sync countries only        |

### Authentication Endpoints (REST)

| Method | Endpoint                     | Description                           |
|--------|------------------------------|---------------------------------------|
| POST   | `/api/v1/auth/signup`               | Register a new user                   |
| POST   | `/api/v1/auth/login`                | Login and get tokens                  |
| POST   | `/api/v1/auth/logout`               | Logout current session                |
| POST   | `/api/v1/auth/token/refresh`        | Refresh access token                  |
| PUT    | `/api/v1/auth/password`             | Change password                       |
| DELETE | `/api/v1/auth/account`              | Delete user account                   |
| DELETE | `/api/v1/auth/sessions/{id}`        | Revoke a specific session             |
| DELETE | `/api/v1/auth/sessions`             | Revoke all other sessions             |
| POST   | `/api/v1/auth/verify-email/send`    | Send email verification               |
| POST   | `/api/v1/auth/forget-password`      | Send password reset email             |
| POST   | `/api/v1/auth/reset-password`       | Reset password using token            |

### Example Usage (cURL)

```bash
# Create a country
curl -X POST "http://0.0.0.0:8000/graphql/v1" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { createCountry(countryCode: \"FR\", countryName: \"France\", capital: \"Paris\", timezone: \"Europe/Paris\", channelCount: 8) { countryCode } }"}'

# Sync all data
curl -X POST "http://0.0.0.0:8000/api/v1/admin/sync/all"
```

> Full cURL examples are available in the [GitHub wiki](https://github.com/HDAI654/TGS/wiki/API%E2%80%90Examples).

---

## 🤝 Contributing

We welcome contributions! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to report issues, propose new features, and submit pull requests.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

We follow [Conventional Commits](https://www.conventionalcommits.org/) and use `black` for code formatting.

---

## 📄 Code of Conduct

We are committed to fostering a welcoming and inclusive community. Please read our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before participating.

---

## 🛡️ License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 🙏 Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com) – the incredible web framework
- [Strawberry](https://strawberry.rocks) – GraphQL made easy
- All open‑source libraries and tools that make this project possible

---

## 📬 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/HDAI654/TGS/issues)
- **Discussions**: [GitHub Discussions](https://github.com/HDAI654/TGS/discussions)

---

**TGS – Stream the world, one request at a time.** 🌍
