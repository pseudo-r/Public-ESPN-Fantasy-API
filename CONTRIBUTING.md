# Contributing to Public-ESPN-Fantasy-API

Thank you for your interest in contributing! This project documents the unofficial ESPN Fantasy API and provides a Django service for consuming it.

## Ways to Contribute

### 📖 Documentation
- Add or correct endpoint URLs, views, or query parameters
- Add missing sport-specific data (e.g., FHL stat IDs, FBA lineup slot IDs)
- Improve response schema examples in `docs/response_schemas.md`
- Document newly discovered endpoints or view parameters
- Fix typos, outdated information, or broken examples

### 🐛 Report a Broken Endpoint
Open an issue using the **🐛 Bug Report** template. Please include:
- The full endpoint URL
- The view parameter(s) you used
- The expected vs actual response (status code + JSON snippet)

### 🔍 Report a Missing Endpoint
Open an issue using the **🔍 Missing View / Endpoint** template. If you've found an ESPN Fantasy API view or endpoint not documented here, we want to know!

### 💻 Code (`fantasy_service`)
Fix bugs or add features to the Django service. Please include tests for any code changes.

---

## Development Setup

### 🐳 Docker (recommended)

```bash
git clone https://github.com/pseudo-r/Public-ESPN-Fantasy-API.git
cd Public-ESPN-Fantasy-API/fantasy_service

cp .env.example .env
# Edit .env: add your ESPN_S2 and SWID cookies

docker compose up --build
```

API at **http://localhost:8001** · Swagger UI at **http://localhost:8001/api/docs/**

### 🐍 Local (without Docker)

Prerequisites: Python 3.12+, PostgreSQL, Redis.

```bash
cd fantasy_service
python -m venv venv && venv\Scripts\activate
pip install -e ".[dev]"

cp .env.example .env

python manage.py migrate
python manage.py runserver 8001
```

### Getting ESPN Credentials

```
1. Log in to fantasy.espn.com
2. Open DevTools → Application → Cookies → https://fantasy.espn.com
3. Copy the values of espn_s2 and SWID
4. Paste them into your .env file
```

---

## Pull Request Guidelines

1. **Branch off `main`**
2. **One concern per PR** — keep changes focused
3. **Write clear commit messages** — reference the view, endpoint, or sport you changed
4. **Add tests** for any `fantasy_service` code changes
5. **Update docs** if you discover new endpoint behavior

### Commit message format

```
type: short description

- Bullet detail if needed
```

Types: `docs`, `feat`, `fix`, `test`, `chore`

---

## Documentation Style Guide

### Endpoint tables

```markdown
| View | Description | Key Response Fields | Status |
|------|-------------|---------------------|--------|
| `mSettings` | League configuration | `settings` | VERIFIED |
```

### Verification labels

- **VERIFIED** — confirmed against a live API response
- **PARTIALLY VERIFIED** — confirmed via community source code or partial live testing
- **UNVERIFIED** — sourced from community docs or inference only

### Curl examples

- Always use `https://lm-api-reads.fantasy.espn.com` (preferred for programmatic access)
- Add a comment above each example
- Include real game codes (`ffl`, `fba`, `flb`, `fhl`) not `{gameCode}` in example values

### File locations

| What | Where |
|------|-------|
| League + view endpoints | `docs/leagues.md` |
| Player pool + kona views | `docs/players.md` |
| Matchups and scoring | `docs/matchups.md` |
| Draft history | `docs/draft.md` |
| Transactions and waivers | `docs/transactions.md` |
| League settings | `docs/settings.md` |
| Historical seasons | `docs/historical_seasons.md` |
| Stat category IDs | `docs/stat_ids.md` |
| Known issues | `docs/known_issues.md` |
| JSON response shapes | `docs/response_schemas.md` |

---

## Code of Conduct

Be kind and respectful. This is a community documentation resource — everyone is welcome regardless of skill level.

---

## License

By contributing, you agree that your contributions will be licensed under the same [MIT License](LICENSE) as this project.
