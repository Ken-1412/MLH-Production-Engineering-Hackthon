# Incident Response & Observability

## Monitoring and Logs (Bronze)
Our application exposes health and status via the `/health` endpoint. All logs are handled by Docker and Gunicorn, formatted to `stdout/stderr` so they can be easily aggregated by a log router like fluentd or CloudWatch.

**Remote Log Inspection:**
Operators can remotely inspect real-time logs via Docker:
`docker logs --tail 100 -f <container_name>`

## Alerts & Routing (Silver)
We define critical alerts using Prometheus rules (`alerts.yml`).
**Key Alerts:**
*   **HighErrorRate:** Triggers when >5% of requests return `5xx` status codes.
*   **HighLatency:** Triggers when p95 latency exceeds 500ms.
*   **DatabaseDown:** Triggers when the database container fails its liveness probe.

**Routing Mechanism:**
Alertmanager is configured to route `severity: critical` alerts directly to an on-call PagerDuty schedule, while `severity: warning` alerts are routed to the `#eng-alerts` Slack channel to ensure issues are addressed within our 15-minute response target.

## Diagnosis Runbook (Gold)
**Simulated Incident: 503 Database Unavailable**
1.  **Alert Fired:** PagerDuty pages the on-call engineer at 3:00 AM due to a `DatabaseDown` and subsequent `HighErrorRate` (503s on all API endpoints).
2.  **Diagnosis:** The engineer checks the Grafana dashboard and observes the Postgres metrics are blank. They remotely SSH and run `docker ps`, seeing the `db` container has `Exited (137)`.
3.  **Log Review:** `docker logs hackathon_db` reveals the container ran out of memory (OOM).
4.  **Mitigation:** The engineer adjusts the `deploy.resources.limits.memory` in `docker-compose.yml`, commits the fix, and runs `docker compose up -d` to restart the database.
5.  **Recovery:** The web containers automatically reconnect via their built-in retry logic in `database.py`. The `/health` endpoint returns `200 OK (connected)`.
6.  **Post-Mortem:** Added alerting on memory pressure to catch OOMs *before* they crash the container.
