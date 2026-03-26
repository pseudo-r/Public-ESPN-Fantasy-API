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

## Query Parameters Reference

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `view` | string | Data section to return (repeat for multiple) | `?view=mTeam&view=mRoster` |
| `scoringPeriodId` | integer | Week (football) or day (baseball/basketball/hockey) | `?scoringPeriodId=1` |
| `matchupPeriodId` | integer | The matchup number in the league schedule | `?matchupPeriodId=1` |
| `seasonId` | integer | Override season year (usually set in path) | `?seasonId=2024` |

> **Note:** `scoringPeriodId` and `matchupPeriodId` are generally required when fetching `mRoster`, `mMatchupScore`, `mTransactions2`, or `mBoxscore`.

---

*Last Updated: March 2026 · 4 sports · 4 game codes · 19 views documented · API version tested live (v1 dead, v2 dead, v3 on lm-api-reads ✅) · Verified via live browser HTTP tests + espn-api source analysis*
