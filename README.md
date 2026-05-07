# Library API - Lab 8

Лабораторна робота 8: створення mock API з використанням Stoplight Prism.

Проект базується на попередніх лабораторних: реальний FastAPI застосунок має JWT authentication, Redis rate limiter і MongoDB. Для цієї лабораторної додано окремий mock-сервіс `mock_api`, який читає `openapi.yaml` і запускає mock server через Prism.

## Що реалізовано

- OpenAPI YAML специфікація у файлі `openapi.yaml`;
- Docker Compose service `mock_api`;
- запуск Prism через command у `docker-compose.yml`;
- mock API доступний на порті `4010`;
- реальний FastAPI API доступний на порті `8000`;
- у mock API описані Auth, Books, root endpoint, помилки 401/404/422/429.

## Запуск

```bash
docker compose up --build
```

Після запуску будуть доступні:

```text
Real API: http://127.0.0.1:8000/docs
Mock API: http://127.0.0.1:4010
```

## Prism service

У `docker-compose.yml` додано:

```yaml
mock_api:
  image: stoplight/prism:latest
  command: mock -h 0.0.0.0 --multiprocess=false /tmp/openapi.yaml
  volumes:
    - ./openapi.yaml:/tmp/openapi.yaml:ro
  ports:
    - "4010:4010"
```

Пояснення:

- `stoplight/prism:latest` - Docker image з Prism;
- `mock` - команда запуску mock server;
- `-h 0.0.0.0` - потрібно, щоб сервер був доступний поза контейнером;
- `--multiprocess=false` - вимикає multiprocess режим Prism, щоб контейнер стабільно працював у Docker;
- `/tmp/openapi.yaml` - YAML специфікація API всередині контейнера;
- `4010:4010` - порт mock API.

## Як перевірити mock API

Root endpoint:

```bash
curl http://127.0.0.1:4010/
```

Login mock:

```bash
curl -X POST http://127.0.0.1:4010/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"student\",\"password\":\"password123\"}"
```

Books mock:

```bash
curl http://127.0.0.1:4010/books/ \
  -H "Authorization: Bearer mock-access-token"
```

Prism не виконує реальну бізнес-логіку і не працює з MongoDB. Він читає `openapi.yaml`, перевіряє, чи запит відповідає специфікації, і повертає приклади відповідей.

## Основні файли

```text
openapi.yaml           # OpenAPI специфікація для Prism
docker-compose.yml     # real API + MongoDB + Redis + Prism mock API
main.py                # реальний FastAPI app
api/auth.py            # auth endpoints
api/books.py           # protected books endpoints
core/rate_limiter.py   # Redis rate limiter
core/security.py       # JWT логіка
```

## Перемикання між лабораторними

```bash
git checkout lab-5
git checkout lab-6
git checkout lab-7
git checkout lab-8
```

Після перемикання:

```bash
docker compose down
docker compose up --build
```

## Що сказати викладачу

У цій лабораторній створено mock API для бібліотеки через Stoplight Prism. Я описав наш API у `openapi.yaml`, додав у Docker Compose окремий сервіс `mock_api`, який запускає команду `prism mock`, підключає YAML-файл зі специфікацією і відкриває mock server на порті `4010`.
