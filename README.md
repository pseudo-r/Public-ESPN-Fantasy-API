# ESPN Fantasy API Documentation

**Disclaimer:** This is documentation for ESPN's undocumented internal Fantasy API. I am not affiliated with ESPN. Use responsibly and follow ESPN's terms of service.

---

## ☕ Support This Project

If this documentation has saved you time, consider supporting ongoing development and maintenance:

| Platform | Link |
|----------|------|
| ☕ Buy Me a Coffee | [buymeacoffee.com/pseudo_r](https://buymeacoffee.com/pseudo_r) |
| 💖 GitHub Sponsors | [github.com/sponsors/Kloverdevs](https://github.com/sponsors/Kloverdevs) |
| 💳 PayPal Donate | [PayPal (CAD)](https://www.paypal.com/donate/?business=H5VPFZ2EHVNBU&no_recurring=0&currency_code=CAD) |

Every contribution helps keep this project updated as ESPN changes their API.

---

## Table of Contents

- [Overview](#overview)
- [Base URLs](#base-urls)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Game Codes](#game-codes)
- [Segments](#segments)
- [Endpoint Catalog](#endpoint-catalog)
  - [League Endpoints](#league-endpoints)
  - [View Parameters](#view-parameters)
  - [Free Agent / Player Endpoints](#free-agent--player-endpoints)
  - [Game & Season Metadata](#game--season-metadata)
- [Query Parameters Reference](#query-parameters-reference)
- [docs/leagues.md](docs/leagues.md)
- [docs/players.md](docs/players.md)
- [docs/matchups.md](docs/matchups.md)
- [docs/draft.md](docs/draft.md)
- [docs/transactions.md](docs/transactions.md)
- [docs/settings.md](docs/settings.md)
- [docs/historical_seasons.md](docs/historical_seasons.md)
- [docs/stat_ids.md](docs/stat_ids.md)
- [docs/known_issues.md](docs/known_issues.md)
- [docs/response_schemas.md](docs/response_schemas.md)

---

## Overview

ESPN operates an undocumented internal API that powers `fantasy.espn.com` and the ESPN Fantasy mobile apps across all four fantasy sports.

**✅ Active API domain:** `https://lm-api-reads.fantasy.espn.com`  
**❌ v1, v2:** Dead — return HTML redirect regardless of headers  
**⚠️ v3 on `fantasy.espn.com`:** Unreliable — redirects to HTML without spoofed browser headers

**All endpoints are REST-style GET requests returning JSON. No official SDK or documentation exists.**

### Important Notes

- **Unofficial:** Not publicly documented; may change without notice
- **Public vs. Private:** Leagues set as "publicly viewable" in their settings return data without authentication. Private leagues require cookies.
- **No Rate Limiting Published:** No official limits. Implement caching and exponential backoff.
- **Season-scoped:** All league data is scoped to a specific season year. You must know the `seasonId`.

---

## Base URLs

> [!IMPORTANT]
> **Only one domain/version combination is functional.** This was verified by live HTTP tests on 2026-03-26.

| API Version | Domain | Status | Notes |
|-------------|--------|--------|-------|
| v1 | `fantasy.espn.com` | ❌ **DEAD** | Redirects to HTML welcome page |
| v2 | `fantasy.espn.com` | ❌ **DEAD** | Redirects to HTML welcome page |
| v3 | `fantasy.espn.com` | ⚠️ **UNRELIABLE** | Redirects to HTML without browser-spoofed headers |
| **v3** | **`lm-api-reads.fantasy.espn.com`** | ✅ **ACTIVE** | Returns JSON reliably — **use this** |

**Always use:**
```
https://lm-api-reads.fantasy.espn.com/apis/v3/games/{gameCode}/seasons/{seasonId}/segments/0/leagues/{leagueId}
```

See [docs/known_issues.md](docs/known_issues.md) for the full live test results.

---

## Quick Start

```bash
# Fantasy Baseball — public league settings (league 101, season 2025)
curl "https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb/seasons/2025/segments/0/leagues/101?view=mSettings"

# Fantasy Baseball — public league teams
curl "https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb/seasons/2025/segments/0/leagues/101?view=mTeam"

# Fantasy Baseball — draft detail
curl "https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb/seasons/2025/segments/0/leagues/101?view=mDraftDetail"

# Football — private league (requires cookies)
curl "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=mSettings" \
  --cookie "espn_s2=YOUR_ESPN_S2; SWID=YOUR_SWID"

# Game metadata — all sports
curl "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl"
curl "https://lm-api-reads.fantasy.espn.com/apis/v3/games/fba"
curl "https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb"
curl "https://lm-api-reads.fantasy.espn.com/apis/v3/games/fhl"
```

---

## Authentication

See [docs/authentication.md](docs/authentication.md) for full details.

**Private leagues** require two cookies sent with every request:

| Cookie | Description |
|--------|-------------|
| `espn_s2` | Long-lived session token (alphanumeric, 200+ chars) |
| `SWID` | ESPN user ID in curly-brace format, e.g. `{A3EBBDAE-5F79-46FF-86EF-7356ABA27F8E}` |

**Finding your cookies:**
1. Log in to `fantasy.espn.com`
2. Open DevTools → Application → Cookies → `fantasy.espn.com`
3. Copy the value of `espn_s2` and `SWID`

**Example (curl):**
```bash
curl "https://fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=mSettings" \
  --cookie "espn_s2=YOUR_ESPN_S2; SWID=YOUR_SWID"
```

**Public league error for missing auth:**
```json
{
  "messages": ["You are not authorized to view this League."],
  "details": [{
    "message": "You are not authorized to view this League.",
    "shortMessage": "You are not authorized to view this League.",
    "type": "AUTH_LEAGUE_NOT_VISIBLE"
  }]
}
```

---

## Game Codes

ESPN Fantasy uses sport-specific game codes in all endpoints:

| Sport | Code | `proSportName` | Active |
|-------|------|----------------|--------|
| Fantasy Football | `ffl` | `football` | ✅ |
| Fantasy Basketball | `fba` | `basketball` | ✅ |
| Fantasy Baseball | `flb` | `baseball` | ✅ |
| Fantasy Hockey | `fhl` | `hockey` | ✅ |

**Current season IDs (as of March 2026):**

| Game | `currentSeasonId` |
|------|-------------------|
| FFL | `2026` |
| FBA | `2026` |
| FLB | `2026` |
| FHL | `2026` |

---

## Segments

All league endpoints include a `segments/{segmentId}` path component. Segment `0` represents the full regular season and is used for all standard queries.

| Segment | Description |
|---------|-------------|
| `0` | Full season (use for all standard requests) |
| `1` | Playoff round 1 (sport-dependent) |
| `2` | Playoff round 2 (sport-dependent) |
| `3` | Championship round (sport-dependent) |

> In practice, nearly all integrations use `segments/0`.

---

## Endpoint Catalog

### League Endpoints

```
GET https://fantasy.espn.com/apis/v3/games/{gameCode}/seasons/{seasonId}/segments/0/leagues/{leagueId}
```

**Path parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `gameCode` | string | `ffl`, `fba`, `flb`, or `fhl` |
| `seasonId` | integer | Season year, e.g. `2025` |
| `leagueId` | integer | Your league ID (visible in the URL on fantasy.espn.com) |

All data is provided via the `view` query parameter. Multiple views can be requested in a single call by repeating the param:  
`?view=mTeam&view=mRoster`

---

### View Parameters

| View | Description | Key Response Fields | Status |
|------|-------------|---------------------|--------|
| `mSettings` | League config, scoring rules, roster slots, draft settings | `settings` | VERIFIED |
| `mTeam` | All teams: names, owners, records, division | `teams`, `members` | VERIFIED |
| `mRoster` | All team rosters with player entries and lineup slots | `teams[].roster.entries` | VERIFIED |
| `mMatchupScore` | Schedule and scores for a given matchup period | `schedule` | VERIFIED |
| `mMatchup` | Older alias for matchup data (same as `mMatchupScore`) | `schedule` | VERIFIED |
| `mScoreboard` | Scoreboard for current scoring period | `scoringPeriodId`, `schedule` | VERIFIED |
| `mStandings` | Standings with W/L/T, pointsFor, pointsAgainst per team | `teams[].record` | VERIFIED |
| `mSchedule` | Full season schedule for all teams, no period filter needed | `schedule` | VERIFIED |
| `mBoxscore` | Per-player scoring breakdown for a matchup | `schedule[].home/away` | VERIFIED |
| `mLiveScoring` | Real-time live scores during active periods; combine with mBoxscore | `schedule[]` | VERIFIED |
| `mDraftDetail` | Full draft history (picks, player IDs, team IDs, order) | `draftDetail` | VERIFIED |
| `mTransactions2` | All transactions: waivers, trades, free agent adds | `transactions` | VERIFIED |
| `mStatus` | High-level league status (drafted, in playoffs, etc.) | `status` | VERIFIED |
| `kona_player_info` | Player pool: stats, ownership, projections, health status | `players` | VERIFIED |
| `kona_playercard` | Deep per-player stats by player ID (needs `X-Fantasy-Filter`) | player entries | PARTIALLY VERIFIED |
| `mPositionalRatings` | Defense vs. position rankings for start/sit decisions | `positionAgainstOpponent` | PARTIALLY VERIFIED |
| `proTeamSchedules_wl` | NFL/NBA/MLB/NHL pro team schedule (bye weeks) | `proTeamSchedules` | VERIFIED |
| `kona_league_messageboard` | League message board (`/communication` sub-path) | topics | PARTIALLY VERIFIED |
| `modular` | ESPN website meta-modules (not recommended for programmatic use) | varies | PARTIALLY VERIFIED |

**Combined views example (recommended — reduces round trips):**
```bash
# Teams + Rosters + Standings in one request (FFL, scoring period 1)
curl "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=mTeam&view=mRoster&view=mStandings&scoringPeriodId=1"

# Live scoring during an active week
curl "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=mBoxscore&view=mLiveScoring&view=mScoreboard&scoringPeriodId=5"
```

### Historical Seasons Endpoint

For seasons before 2018, a different URL pattern is required:

```bash
# Pre-2018 (leagueHistory format)
GET https://lm-api-reads.fantasy.espn.com/apis/v3/games/{gameCode}/leagueHistory/{leagueId}?seasonId={year}&view=mSettings
```

Response is a **JSON array** — use `response[0]`. See [docs/historical_seasons.md](historical_seasons.md) for full details.

### Sub-Path Endpoints

These use different URL patterns:

```bash
# All active players for a sport/season (for player ID → name mapping)
GET https://lm-api-reads.fantasy.espn.com/apis/v3/games/{gameCode}/seasons/{seasonId}/players?view=players_wl
# + Header: X-Fantasy-Filter: {"filterActive": {"value": true}}

# Player news
GET https://lm-api-reads.fantasy.espn.com/apis/v3/games/{gameCode}/news/players?playerId={id}

# League message board
GET https://lm-api-reads.fantasy.espn.com/apis/v3/games/{gameCode}/seasons/{seasonId}/segments/0/leagues/{leagueId}/communication?view=kona_league_messageboard
```

---

### Free Agent / Player Endpoints

Player pool data comes from `kona_player_info`. To filter for free agents or waivers, pass a JSON filter in the `X-Fantasy-Filter` request header:

```bash
curl "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=kona_player_info&scoringPeriodId=1" \
  -H 'X-Fantasy-Filter: {"players":{"filterStatus":{"value":["FREEAGENT","WAIVERS"]},"filterSlotIds":{"value":[0,2,4,6,17,16]},"limit":50,"sortPercOwned":{"sortPriority":1,"sortAsc":false}}}'
```

**Common `filterStatus` values:**

| Value | Description |
|-------|-------------|
| `FREEAGENT` | Available free agents |
| `WAIVERS` | On waivers |
| `ONTEAM` | Rostered by a team |
| `FREEAGENT,WAIVERS` | Combined free agent + waiver pool |

---

### Game & Season Metadata

These endpoints do not require a league ID and are always public:

```bash
# Game info (all fantasy sports)
GET https://lm-api-reads.fantasy.espn.com/apis/v3/games/{gameCode}

# Season info
GET https://lm-api-reads.fantasy.espn.com/apis/v3/games/{gameCode}/seasons/{seasonId}
```

**Game info response (`/apis/v3/games/ffl`):**
```json
{
  "abbrev": "FFL",
  "active": true,
  "currentSeasonId": 2026,
  "name": "Fantasy Football",
  "proSportName": "football"
}
```

**Season info response (`/apis/v3/games/flb/seasons/2025`):**
```json
{
  "abbrev": "FLB 2025",
  "active": true,
  "startDate": 1711350000000,
  "endDate": ...,
  "currentScoringPeriod": {
    "id": 196
  }
}
```

---

## Additional Domains / Related Endpoint Families

ESPN operates several distinct API domains beyond the main Fantasy API. This section catalogs every discovered domain, explains what each one is used for, its access level, and how it connects to the Fantasy API.

---

### 1. `lm-api-reads.fantasy.espn.com` — ✅ PRIMARY (Fantasy Read API)

**What it is:** The main internal read API for all ESPN Fantasy sports data. This is the domain documented throughout this repository.

**Access:** Public (no auth for public leagues) / Cookies required for private leagues and historical data.

**Example endpoints:**
```
GET https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=mSettings
GET https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb/seasons/2025/players?view=players_wl
GET https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl
```

**Relationship:** This IS the main Fantasy API. All documented views, game codes, and endpoints in this repository use this domain.

---

### 2. `lm-api-writes.fantasy.espn.com` — ⚠️ WRITE API (Discovered, Not Documented)

**What it is:** The write/mutation counterpart — handles waiver claims, trade proposals, lineup changes, and other state-modifying fantasy operations. Observed in browser network traffic when performing actions on `fantasy.espn.com`.

**Access:** Private — requires authenticated cookies (`espn_s2` + `SWID`). All write operations require an active session.

**Example endpoints (observed, not verified):**
```
POST https://lm-api-writes.fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}/transactions/
POST https://lm-api-writes.fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}/roster/
```

**Relationship:** The write-side partner of `lm-api-reads`. Together they form the full Fantasy League Manager (LM) API. This repository does **not** document the write API.

> [!CAUTION]
> Do not automate lineup changes, trades, or waiver claims at scale. ESPN may ban accounts engaging in automated write operations.

---

### 3. `sports.core.api.espn.com` — ✅ PRO SPORTS CORE DATA

**What it is:** ESPN's canonical sports reference API. Returns professional sports entity data — leagues, teams, athletes, venues, events, and season structures across all major sports.

**Access:** Public (no authentication required)

**Example endpoints:**
```
GET https://sports.core.api.espn.com/v2/sports/football/leagues/nfl
GET https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/athletes
GET https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2025/athletes/{athleteId}
GET https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/seasons/2025/teams
```

**Relationship to Fantasy API:** The Fantasy API references pro team IDs (`proTeamId`) and player IDs (`playerId`) that map to this domain. Use it to resolve player headshots, biographical data, career stats, and pro schedule information not returned by the Fantasy API.

---

### 4. `site.api.espn.com` — ✅ ESPN SITE DATA (Scoreboards, News, Standings)

**What it is:** The ESPN website's primary data API — powers scoreboards, news feeds, league standings, game summaries, and box scores across all ESPN sports.

**Access:** Public (no authentication required)

**Example endpoints:**
```
GET https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard
GET https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/news
GET https://site.api.espn.com/apis/site/v2/sports/basketball/nba/standings
GET https://site.api.espn.com/apis/v2/sports/hockey/nhl/standings
GET https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard?dates=20250401
```

**Relationship to Fantasy API:** Provides real-world game data that drives fantasy scoring. Use this domain to check whether an NFL game is currently live (to decide whether to poll `mLiveScoring`), or to get injury news not yet reflected in the Fantasy API's `injuryStatus` field.

---

### 5. `site.web.api.espn.com` — ✅ ESPN WEB APP API

**What it is:** A web-app-facing variant of the ESPN site API with enriched, pre-aggregated data for ESPN's web UI — often includes full game summaries and play-by-play context.

**Access:** Public (no authentication required)

**Example endpoints:**
```
GET https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event={gameId}&region=us&lang=en
GET https://site.web.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard
```

**Relationship to Fantasy API:** Provides richer game summaries and play-by-play data supplementing fantasy boxscore data. Where the Fantasy API tells you a player scored 24.5 points, this domain gives you the underlying stat lines.

---

### 6. `now.core.api.espn.com` — ⚠️ LIVE / REAL-TIME DATA

**What it is:** ESPN's live and near-real-time data stream API. Used for polling active game state and in-progress score updates.

**Access:** Public (unverified — may require browser-like headers)

**Example endpoints (observed):**
```
GET https://now.core.api.espn.com/v1/sports/news
GET https://now.core.api.espn.com/v1/sports/football/nfl/live
```

**Relationship to Fantasy API:** Real-time companion to the Fantasy API's `mLiveScoring` view. During active scoring periods, `mLiveScoring` on `lm-api-reads` ultimately reflects data sourced from ESPN's live infrastructure, which this domain exposes more directly.

---

### 7. `a.espncdn.com` / `cdn.espn.com` — ✅ CDN / CACHED ASSETS

**What it is:** ESPN's content delivery network for static and semi-static cached data — player headshots, team logos, and pre-rendered media assets.

**Access:** Public (no authentication required)

**Example asset URLs:**
```
https://a.espncdn.com/i/headshots/nfl/players/full/{playerId}.png
https://a.espncdn.com/combiner/i?img=/i/teamlogos/nfl/500/{teamAbbrev}.png
```

**Relationship to Fantasy API:** The Fantasy API returns `playerId` and `proTeamId` integers. Construct headshot and logo URLs against the CDN to display player images in a UI built on top of the Fantasy API:
```python
headshot = f"https://a.espncdn.com/i/headshots/nfl/players/full/{player_id}.png"
logo     = f"https://a.espncdn.com/combiner/i?img=/i/teamlogos/nfl/500/{team_abbrev}.png"
```

---

### Domain Summary Table

| Domain | Purpose | Auth Required | Fantasy Relevance |
|--------|---------|---------------|-------------------|
| `lm-api-reads.fantasy.espn.com` | Fantasy league data (read) | Cookies for private leagues | ⭐ Primary — all docs here |
| `lm-api-writes.fantasy.espn.com` | Fantasy league mutations (write) | Always required | Write ops (not documented) |
| `sports.core.api.espn.com` | Pro sports reference data | None | Player/team ID resolution |
| `site.api.espn.com` | Scoreboards, news, standings | None | Injury & score context |
| `site.web.api.espn.com` | Web-app game summaries, play-by-play | None | Stat line supplementation |
| `now.core.api.espn.com` | Real-time live game data | None (unverified) | Live scoring support |
| `a.espncdn.com` | Static assets (headshots, logos) | None | UI image assets |

---

## Query Parameters Reference

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `view` | string | Data section to return (repeat for multiple) | `?view=mTeam&view=mRoster` |
| `scoringPeriodId` | integer | Week (football) or day (baseball/basketball/hockey) | `?scoringPeriodId=1` |
| `matchupPeriodId` | integer | The matchup number in the league schedule | `?matchupPeriodId=1` |
| `seasonId` | integer | Override season year (usually set in path) | `?seasonId=2024` |

> **Note:** `scoringPeriodId` and `matchupPeriodId` are generally required when fetching `mRoster`, `mMatchupScore`, `mTransactions2`, or `mBoxscore`.

---

*Last Updated: March 2026 · 4 sports · 4 game codes · 19 views documented · 7 ESPN domains catalogued · API version tested live (v1 dead, v2 dead, v3 on lm-api-reads ✅) · Verified via live browser HTTP tests + espn-api source analysis*
