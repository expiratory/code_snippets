# Code Snippets

Personal code snippets library. Manage and run your code snippets.

Backend - FastAPI, PostgreSQL, SQLAlchemy, Alembic, Poetry, Pytest, Docker (for running code)

Frontend - React, TS, Vite, Tailwind, Lucide

Also uses RabbitMQ, Elasticsearch, Redis

Auth - JWT + Refresh tokens, also uses Google OAuth 2.0

## Local Quick Start

At project root directory

- Create your .env file
```bash
cp .example.env .env
```

- Up containers
```bash
docker compose -f 'docker-compose.dev.yml' up -d --build
```

- Apply migrations
```bash
docker compose exec app alembic upgrade head
```

- Make new migrations
```bash
docker compose exec app alembic revision --autogenerate -m "message"
```

- Run tests
```bash
docker compose exec app pytest --cov=app tests/
```

- Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to .env file.
App would be using only username and email from Google account.
For your client in Google Auth Platform you should use this Redirect URI (local dev):
```
http://localhost:8000/auth/google/callback
```

By default at your localhost:

Frontend is up on 3000 port

Backend is up on 8000 port

Swagger - /docs
