# Failure Modes — MLH PE Hackathon 2026

## 1. Database connection lost mid-request

| | |
|---|---|
| **Trigger** | DB goes down while the web process is running |
| **System behavior** | Route catches `OperationalError` / `DatabaseError` |
| **HTTP response** | `503 {"error": "Database unavailable", "code": 503}` |
| **Client sees** | Clean JSON, never a Python traceback |
| **Auto-recovery** | Yes — next request succeeds once DB is back |
| **Tested by** | `app/routes/urls.py` DB error handlers; `app/__init__.py` unhandled exception handler |

---

## 2. Database unavailable at container startup

| | |
|---|---|
| **Trigger** | Web container starts before DB is ready |
| **System behavior** | `init_db()` creates the proxy; `before_request` hook attempts connection |
| **HTTP response** | `/health` returns `200 {"status": "ok", "db": "disconnected"}` |
| **Client sees** | Process is alive, health check passes, DB status is transparent |
| **Auto-recovery** | Yes — once DB is up, `before_request` connects successfully |
| **Tested by** | `docker-compose.yml` uses `depends_on: condition: service_healthy`; `/health` always returns 200 |

---

## 3. POST with a duplicate unique field

| | |
|---|---|
| **Trigger** | POST `/urls` with a `short_code` that already exists in the database |
| **System behavior** | `Url.create()` raises `IntegrityError`, caught explicitly in route |
| **HTTP response** | `409 {"error": "Resource already exists", "code": 409}` |
| **Client sees** | Clean JSON error with 409 status — never 500, never a traceback |
| **Auto-recovery** | N/A — client must use a different `short_code` |
| **Tested by** | `tests/test_urls.py::test_create_duplicate_returns_409` |

---

## 4. POST with a missing required field

| | |
|---|---|
| **Trigger** | POST `/urls` with missing `short_code`, `original_url`, `title`, or `user_id` |
| **System behavior** | `_validate_create()` detects missing fields before touching DB |
| **HTTP response** | `400 {"error": "Validation failed", "fields": {"short_code": "required", ...}, "code": 400}` |
| **Client sees** | Field-level error detail explaining exactly which fields are missing |
| **Auto-recovery** | N/A — client must provide all required fields |
| **Tested by** | `tests/test_urls.py::test_create_missing_required_field_returns_400`, `test_create_with_missing_short_code_returns_field_error` |

---

## 5. POST with wrong field type (e.g. user_id = "banana")

| | |
|---|---|
| **Trigger** | POST `/urls` with `user_id` set to a non-numeric string |
| **System behavior** | `_validate_create()` catches `ValueError` during `int()` conversion |
| **HTTP response** | `400 {"error": "Validation failed", "fields": {"user_id": "must be an integer"}, "code": 400}` |
| **Client sees** | Clean JSON error with specific field-level feedback |
| **Auto-recovery** | N/A — client must send correct types |
| **Tested by** | `tests/test_urls.py::test_create_invalid_type_returns_400` |

---

## 6. GET /urls/999999 — ID does not exist

| | |
|---|---|
| **Trigger** | GET request for an ID that has no matching row in the database |
| **System behavior** | `Url.safe_get(999999)` catches `DoesNotExist` and returns `None` |
| **HTTP response** | `404 {"error": "Not found", "code": 404}` |
| **Client sees** | Clean JSON 404 — never an empty response or HTML |
| **Auto-recovery** | N/A — the resource simply doesn't exist |
| **Tested by** | `tests/test_urls.py::test_get_nonexistent_id_returns_404` |

---

## 7. GET /urls/abc — ID is not an integer

| | |
|---|---|
| **Trigger** | GET request with a non-numeric string as the record ID |
| **System behavior** | `Url.safe_get("abc")` catches `ValueError` from `int("abc")` and returns `None` |
| **HTTP response** | `404 {"error": "Not found", "code": 404}` |
| **Client sees** | Clean JSON — never a 500, never HTML, never a Python traceback |
| **Auto-recovery** | N/A — client must use a valid integer ID |
| **Tested by** | `tests/test_urls.py::test_get_string_id_returns_404`, `test_error_responses_never_return_html` |

---

## 8. Request body is empty or not valid JSON

| | |
|---|---|
| **Trigger** | POST/PUT with `Content-Type: application/json` but body is `"not json"` or empty |
| **System behavior** | `request.get_json(silent=True)` returns `None`, route returns 400 immediately |
| **HTTP response** | `400 {"error": "Request body must be valid JSON", "code": 400}` |
| **Client sees** | Clean JSON error explaining the body is invalid |
| **Auto-recovery** | N/A — client must send valid JSON |
| **Tested by** | `tests/test_urls.py::test_create_no_body_returns_400` |

---

## 9. Container process killed

| | |
|---|---|
| **Trigger** | `docker kill <web_container_id>` — simulates OOM kill or crash |
| **System behavior** | Docker detects the container exited. `restart: always` in `docker-compose.yml` triggers automatic restart. |
| **HTTP response** | During the ~5–10 second restart window: connection refused. After recovery: normal 200 responses. |
| **Client sees** | Brief downtime (typically < 10 seconds), then full recovery with no data loss |
| **Auto-recovery** | Yes — `restart: always` is the key. Docker restarts the container automatically. |
| **Kill command** | `docker kill $(docker ps --filter "name=web" -q \| head -1)` |
| **Expected recovery time** | 5–10 seconds |
| **Tested by** | `scripts/chaos_test.sh` steps 4–6 |

---

## 10. Two simultaneous POSTs with identical unique field (race condition)

| | |
|---|---|
| **Trigger** | Two concurrent `POST /urls` requests with the same `short_code` arrive at nearly the same time |
| **System behavior** | Both pass validation (no DB check yet). First `Url.create()` succeeds. Second `Url.create()` hits the `UNIQUE` constraint on `short_code` and raises `IntegrityError`. |
| **HTTP response** | Winner: `201 {"data": {...}}`. Loser: `409 {"error": "Resource already exists", "code": 409}` |
| **Client sees** | Exactly one record created, no data corruption. The losing request gets a clear 409 error. |
| **Auto-recovery** | N/A — the losing client simply retries with a different `short_code` |
| **Data integrity** | PostgreSQL's UNIQUE constraint guarantees no duplicates, regardless of timing |
| **Tested by** | `tests/test_urls.py::test_create_duplicate_returns_409` (sequential simulation) |
