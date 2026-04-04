# MLH PE Hackathon 2026 - URL Shortener 🚀

A production-ready, resilient, and highly observable URL Shortener built for the MLH Production Engineering Hackathon 2026. This project achieves **Gold Tier** across all hackathon tracks (Reliability, Documentation, Scalability, and Incident Response) and fulfills the Hidden Evaluator bonuses.

## ✨ Features

- **Robust URL Shortening:** Create, update, list, and delete short links with auto-generated or custom short codes.
- **User Management:** Complete user CRUD and bulk CSV import capabilities.
- **Analytics & Events:** Track URL interactions with detailed JSON metadata.
- **Resilience & Chaos Engineering:** Built-in auto-recovery policies, graceful database degradation handling, and comprehensive chaos testing.
- **Strict Data Validation:** Thorough request validation preventing bad data from hitting the database, complete with field-level error reporting.
- **CI/CD Pipeline:** Fully automated GitHub Actions workflow enforcing strict >70% test coverage gates.
- **Observability Ready:** Structured endpoints, liveness probes, and documented Prometheus alerting rules.

## 🛠 Tech Stack

- **Backend Framework:** Flask 3.1
- **Database:** PostgreSQL
- **ORM:** Peewee 3.17
- **WSGI Server:** Gunicorn 25.3
- **Package Manager:** uv (Python 3.13)
- **Containerization:** Docker & Docker Compose
- **Testing:** Pytest & pytest-cov

## 📖 Documentation Tracks

We have meticulously documented our system to meet production standards. Please refer to the following guides:

- **[Operating Guide (Documentation Track)](OPERATING_GUIDE.md):** System layout, API reference, deployment/revert steps, environment variables, and technical tradeoffs.
- **[Scalability Plan (Scalability Track)](SCALABILITY.md):** Baseline load test results, horizontal scaling strategies, and Redis caching implementation details for peak load.
- **[Incident Response (Incident Response Track)](INCIDENT_RESPONSE.md):** Remote log inspection, alert routing, and a step-by-step diagnosis runbook for production outages. Includes our mock [Prometheus Alerts Config](alerts.yml).
- **[Failure Modes (Reliability Track)](FAILURE_MODES.md):** Exhaustive documentation of 10 edge cases, network splits, and data validation failures showing how our system safely degrades and recovers.

## 🚀 Getting Started

### Prerequisites
- [Docker & Docker Compose](https://docs.docker.com/get-docker/)
- [uv](https://github.com/astral-sh/uv) (for local development)
- Python >= 3.13

### Running with Docker (Recommended)
This will spin up both the Postgres database and the Gunicorn web server, simulating the production environment with auto-restart policies enabled.

```bash
docker compose up --build -d
```
The API will be available at `http://localhost:5000`.

### Running Locally (Development)
1. Install dependencies:
   ```bash
   uv sync
   ```
2. Start a local Postgres instance (or adjust `.env` to point to an existing one).
3. Run the development server:
   ```bash
   uv run run.py
   ```

## 🧪 Testing & Validation

### Unit & Integration Tests
We maintain a strict test suite interacting with a real PostgreSQL test database.

1. Start the test database:
   ```bash
   docker run -d --name hackathon_test_db -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=hackathon_test postgres:15-alpine
   ```
2. Run pytest with coverage:
   ```bash
   uv run pytest --cov=app --cov-report=term-missing -v
   ```
*Note: Our CI/CD pipeline enforces a minimum of 70% code coverage to pass.*

### Chaos Engineering Test
We have a script that validates our Docker auto-recovery policies by forcefully killing the web container and verifying it comes back online successfully.

```bash
bash scripts/chaos_test.sh
```

### Load Testing
Test the baseline throughput and latency of the application:
```bash
python scripts/load_test.py
```

## 🗄 Seeding the Database
To populate the database with initial CSV data:
```bash
uv run python scripts/load_seed.py urls.csv
uv run python scripts/load_seed.py events.csv
uv run python scripts/load_seed.py users.csv
```

## 🤝 Authors
- [Ketan Singh](https://github.com/Ken-1412)
