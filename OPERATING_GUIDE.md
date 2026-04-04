# Operating Guide & System Documentation

## System Layout
The MLH PE Hackathon URL Shortener is a containerized microservices architecture:
*   **Web API (Flask/Gunicorn):** Handles all incoming HTTP requests, routes, and business logic.
*   **Database (PostgreSQL):** Stores Users, URLs, and Analytics Events. Persisted via Docker volumes.

## API Endpoints
*   `GET /health`: Liveness probe.
*   `POST /users/bulk`: Bulk load users via CSV.
*   `GET /users`, `POST /users`, `GET /users/<id>`, `PUT /users/<id>`: User management.
*   `GET /urls`, `POST /urls`, `GET /urls/<id>`, `PUT /urls/<id>`, `DELETE /urls/<id>`: URL management (includes `?search=` and `?user_id=` filters).
*   `GET /events`: Fetch analytics events.

## Environment Variables
*   `FLASK_DEBUG`: Enables Flask debug mode (must be `false` in production).
*   `DATABASE_NAME`: The Postgres database name.
*   `DATABASE_HOST`: The hostname of the database (e.g., `db` or `localhost`).
*   `DATABASE_PORT`: Postgres port (default `5432`).
*   `DATABASE_USER` / `DATABASE_PASSWORD`: Credentials for Postgres authentication.

## Release and Revert Steps
**To Release:**
1. Merge feature branch to `main`.
2. CI/CD Pipeline automatically runs tests and checks coverage (gatekeeper: `--cov-fail-under=70`).
3. Deploy new Docker image: `docker compose up -d --build`.

**To Revert:**
1. Identify the previous stable commit hash.
2. Run `git revert <commit_hash>`.
3. Push to `main` to trigger the CI/CD pipeline and redeploy.

## Technical Choices & Tradeoffs
*   **Flask over FastAPI/Django:** Chosen for its lightweight nature and simplicity, allowing rapid prototyping for the hackathon. Tradeoff: Lacks built-in async support.
*   **Peewee over SQLAlchemy:** Peewee provides a simpler, more Pythonic ORM syntax which is easier to debug and test quickly.
*   **PostgreSQL:** Chosen for strict ACID compliance and robust `UNIQUE` constraint handling to prevent duplicate `short_code` race conditions.

## Expected Limits & Growth
*   **Database:** The `urls` and `events` tables will grow rapidly. Partitioning the `events` table by month will be required at scale.
*   **Bottlenecks:** The API will become CPU-bound under heavy traffic. We will need to scale out Gunicorn workers and put an Nginx reverse proxy/load balancer in front of multiple web containers.
