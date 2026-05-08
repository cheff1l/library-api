# Library API - Lab 9

Laboratory work 9: API load testing with Locust.

The project is based on previous labs: FastAPI, JWT access/refresh authentication,
Redis rate limiter, MongoDB, and Prism mock API. In this lab a Locust load test is
added and everything is started through Docker Compose.

## What Was Added

- `locustfile.py` with a Locust load test;
- Docker Compose service `locust`;
- Locust Web UI on port `8089`;
- load testing of one endpoint: `POST /auth/login`;
- `RATE_LIMIT_ENABLED=false` for the API container in this branch, so the load
  test checks API performance without being stopped by the rate limiter.

## Run

```bash
docker compose up --build
```

After startup:

```text
FastAPI Swagger: http://127.0.0.1:8000/docs
Locust UI:       http://127.0.0.1:8089
Prism mock API:  http://127.0.0.1:4010
```

## How To Run The Locust Test

1. Open `http://127.0.0.1:8089`.
2. Set users, for example `10`.
3. Set spawn rate, for example `2`.
4. Host should already be `http://api:8000`.
5. Click `Start swarming`.
6. Watch the statistics for `POST /auth/login`.

The test sends this request repeatedly:

```http
POST /auth/login
Content-Type: application/json
```

```json
{
  "username": "student",
  "password": "password123"
}
```

Expected result: most requests should return `200 OK`, and the Locust screen
should show request count, failures, average response time, min/max response
time, and requests per second.

## Main Files

```text
locustfile.py         # Locust load test scenario
docker-compose.yml   # API, MongoDB, Redis, Prism, and Locust services
main.py              # FastAPI application
core/rate_limiter.py # Redis rate limiter with RATE_LIMIT_ENABLED switch
api/auth.py          # Login endpoint tested by Locust
```

## What To Say To The Teacher

In this lab I added load testing with Locust. The test is described in
`locustfile.py`; it creates virtual users that repeatedly call one selected
endpoint, `POST /auth/login`. Locust runs in Docker through the `locust` service
in `docker-compose.yml` and provides a Web UI on port `8089`. For this branch
the rate limiter is disabled with `RATE_LIMIT_ENABLED=false`, because the goal
of the lab is to measure endpoint behavior under load, not to receive `429`
responses from the previous lab.
