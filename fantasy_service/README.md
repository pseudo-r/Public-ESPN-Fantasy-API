# ESPN Fantasy API Service

A production-ready **Django REST API** that ingests data from the [ESPN Fantasy v3 API](../README.md) and exposes it via a clean, documented REST interface. Supports Fantasy Football, Basketball, Baseball, and Hockey.

Modelled after the `espn_service` project in [Public-ESPN-API](../../../Public-ESPN-API).

---

## Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 5, Django REST Framework |
| API Docs | drf-spectacular (Swagger / OpenAPI 3) |
| Async tasks | Celery + Redis |
| HTTP client | httpx + tenacity (retries) |
| Database | PostgreSQL (SQLite for tests) |
| Containerization | Docker + docker-compose |
| Logging | structlog |

---

## Quick Start (Docker)

```bash
# 1. Clone and enter the service directory
cd fantasy_service

# 2. Copy environment file and fill in your ESPN credentials
cp .env.example .env
# Edit .env: set ESPN_S2 and SWID (see docs/authentication.md)

# 3. Start all services (postgres, redis, web, celery)
make up
# or: docker compose up --build -d

# 4. Run migrations
docker compose exec web python manage.py migrate

# 5. Sync your first fantasy league
docker compose exec web python manage.py sync_fantasy \
    --game ffl --season 2025 --league YOUR_LEAGUE_ID

# 6. Browse the API
open http://localhost:8001/api/docs/
```

---

## Quick Start (Local Dev)

```bash
cd fantasy_service
python -m venv venv && venv\Scripts\activate   # Windows
pip install -e ".[dev]"

cp .env.example .env  # fill in your ESPN_S2 and SWID

python manage.py migrate
python manage.py runserver 8001
```

---

## Finding Your League ID

Your ESPN Fantasy league ID is in the URL when you visit your league on fantasy.espn.com:

```
https://fantasy.espn.com/football/league?leagueId=336358
                                                   ^^^^^^
```

---

## Syncing a League

### Via management command (dev/manual)

```bash
# Full sync (all data)
python manage.py sync_fantasy --game ffl --season 2025 --league 336358

# Sync only specific data
python manage.py sync_fantasy --game ffl --season 2025 --league 336358 --only league
python manage.py sync_fantasy --game ffl --season 2025 --league 336358 --only draft
python manage.py sync_fantasy --game flb --season 2025 --league 101 --period 50 --only roster

# Options:
#   --game    ffl | fba | flb | fhl
#   --season  Four-digit year (e.g., 2025)
#   --league  ESPN league ID
#   --period  Scoring period ID (default: 1)
#   --only    league | roster | matchups | draft | transactions | players | all
```

### Via API endpoint (triggers Celery task)

```bash
curl -X POST http://localhost:8001/api/v1/ingest/league/ \
  -H "Content-Type: application/json" \
  -d '{"game_code": "ffl", "season_id": 2025, "league_id": 336358}'
```

---

## API Reference

Interactive docs at: **`http://localhost:8001/api/docs/`**

### Fantasy Data Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/fantasy/games/` | List game types (ffl, fba, flb, fhl) |
| `GET` | `/api/v1/fantasy/leagues/` | List ingested leagues |
| `GET` | `/api/v1/fantasy/leagues/{id}/` | League detail + members |
| `GET` | `/api/v1/fantasy/teams/` | List fantasy teams |
| `GET` | `/api/v1/fantasy/players/` | Player pool (filter by injury status, position) |
| `GET` | `/api/v1/fantasy/roster/` | Roster entries (filter by team, scoring period) |
| `GET` | `/api/v1/fantasy/matchups/` | Matchups (filter by league, period, playoff flag) |
| `GET` | `/api/v1/fantasy/draft/` | Draft picks (filter by league, round) |
| `GET` | `/api/v1/fantasy/transactions/` | Transactions (filter by type, status) |

### Ingest Trigger Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/ingest/league/` | Full league sync (dispatches Celery task) |
| `POST` | `/api/v1/ingest/roster/` | Roster sync for a scoring period |
| `POST` | `/api/v1/ingest/players/` | Player pool sync |
| `POST` | `/api/v1/ingest/transactions/` | Transaction sync for a scoring period |

---

## Docker Services

| Service | Port | Description |
|---------|------|-------------|
| `web` | `8001` | Django dev server |
| `celery` | — | Celery worker (2 concurrent tasks) |
| `postgres` | `5433` | PostgreSQL 16 |
| `redis` | `6380` | Redis 7 (broker + cache) |

```bash
make up       # Start all services
make down     # Stop all services
make worker   # Start Celery worker (local)
```

---

## Authentication

The ESPN Fantasy API requires cookies for private leagues and all historical data. Set them in your `.env`:

```
ESPN_S2=AEB...your_long_cookie...
SWID={A3EBBDAE-5F79-46FF-86EF-7356ABA27F8E}
```

To find these values, open your browser DevTools on `fantasy.espn.com`:
1. **Application** → **Cookies** → `https://fantasy.espn.com`
2. Copy `espn_s2` and `SWID` values

See [docs/authentication.md](../docs/authentication.md) for full details.

---

## Project Structure

```
fantasy_service/
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── manage.py
├── .env.example
├── config/
│   ├── celery.py          # Celery app
│   ├── urls.py            # Root URL config
│   └── settings/
│       ├── base.py        # Shared settings
│       ├── local.py       # Dev overrides
│       └── test.py        # Test (SQLite in-memory)
├── clients/
│   └── fantasy_client.py  # ESPN Fantasy HTTP client
└── apps/
    ├── fantasy/           # Models, serializers, views, admin
    │   ├── models.py      # 9 models (League, Team, Player, ...)
    │   ├── serializers.py
    │   ├── views.py       # 8 ViewSets
    │   ├── admin.py
    │   └── urls.py
    └── ingest/            # Ingestion services, Celery tasks
        ├── services.py    # 6 ingestion service classes
        ├── tasks.py       # 6 Celery tasks + sync_league_full
        ├── views.py       # 4 ingest trigger API views
        ├── urls.py
        └── management/commands/sync_fantasy.py
```
