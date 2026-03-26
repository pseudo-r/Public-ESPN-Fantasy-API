# Known Issues & Instability

This document catalogs known problems, breaking changes, undocumented behaviors, and sport-specific gaps in the ESPN Fantasy API.

---

## Breaking Change History

### April 2024 — Primary Domain Switch

ESPN began routing fantasy API traffic through a new internal domain:

```
# Old (still works but may redirect)
https://fantasy.espn.com/apis/v3/games/{gameCode}/...

# New primary internal domain (more reliable)
https://lm-api-reads.fantasy.espn.com/apis/v3/games/{gameCode}/...
```

**Impact:** Some clients that hardcoded `fantasy.espn.com` began receiving HTML redirect responses instead of JSON. Fix: switch to `lm-api-reads.fantasy.espn.com`, or add `Accept: application/json` headers and ensure `Referer: https://fantasy.espn.com/` is set.

### August 2025 — Historical Data Auth Restriction

ESPN restricted access to historical season data (prior seasons for leagues) that was previously accessible without cookies. After August 1, 2025, retrieving historical data via `leagueHistory` endpoint requires `espn_s2` cookie even for leagues that were previously publicly viewable.

**Impact:** Any tool relying on unauthenticated historical data access broke.

### February 2019 — v2 → v3 Migration

ESPN migrated from a v2 to v3 API, breaking all existing clients. The URL base changed from `/apis/v2/` to `/apis/v3/`, and the response schema was significantly restructured.

**Impact:** All pre-2019 ESPN Fantasy API documentation, libraries, and tools became obsolete. Modern documentation covers only v3.

---

## Live API Version Test Results — 2026-03-26

The following results were captured from real browser HTTP requests against the ESPN Fantasy API to determine which API versions and domains are currently functional.

**Test league used:** FLB league 101 (public, season 2025)

| # | URL | Status | Result |
|---|-----|--------|--------|
| 1 | `https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb/seasons/2025/segments/0/leagues/101?view=mSettings` | **200 OK** | ✅ JSON response — keys: `draftDetail`, `gameId`, `id`, `scoringPeriodId`, `seasonId`, `settings`, `status`, `teams` |
| 2 | `https://fantasy.espn.com/apis/v3/games/flb/seasons/2025/segments/0/leagues/101?view=mSettings` | **HTML Redirect** | ❌ Redirects to `/baseball/welcome` page — API not accessible via direct browser on this domain |
| 3 | `https://fantasy.espn.com/apis/v2/games/flb/seasons/2025/segments/0/leagues/101?view=mSettings` | **HTML Redirect** | ❌ Redirects to `/baseball/welcome` — v2 is dead |
| 4 | `https://fantasy.espn.com/apis/v1/games/flb/seasons/2025/segments/0/leagues/101?view=mSettings` | **HTML Redirect** | ❌ Redirects to `/baseball/welcome` — v1 is dead |
| 5 | `https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/336358?view=mSettings` | **401 Unauthorized** | ⚠️ JSON: "You are not authorized to view this League." — private league, cookies required |
| 6 | `https://lm-api-reads.fantasy.espn.com/apis/v3/games/fba/seasons/2025/segments/0/leagues/101?view=mSettings` | **404 Not Found** | ⚠️ League 101 does not exist for FBA season 2025 |

### Conclusions

> **v1 and v2 are completely dead.** They return HTML redirects regardless of headers.

> **v3 on `fantasy.espn.com`** also returns HTML redirects when accessed directly from a browser or simple HTTP client. It requires spoofed browser headers to get JSON, and is still unreliable.

> **v3 on `lm-api-reads.fantasy.espn.com`** is the only endpoint that reliably returns JSON without header tricks. **Always use this domain.**

### Summary

| API Version | Domain | Status |
|-------------|--------|--------|
| v1 | `fantasy.espn.com` | ❌ DEAD — HTML redirect |
| v2 | `fantasy.espn.com` | ❌ DEAD — HTML redirect |
| v3 | `fantasy.espn.com` | ⚠️ UNRELIABLE — HTML redirect without browser headers |
| v3 | `lm-api-reads.fantasy.espn.com` | ✅ ACTIVE — Returns JSON reliably |

The only version to use: **`/apis/v3/` on `lm-api-reads.fantasy.espn.com`**

---


## Known Endpoint Instabilities

### `fantasy.espn.com` vs `lm-api-reads.fantasy.espn.com`

Direct requests to `fantasy.espn.com/apis/v3/...` from non-browser clients (curl, Python requests, etc.) may receive HTML redirect responses because of bot-detection middleware. This is intermittent.

**Symptoms:** Response content begins with `<!DOCTYPE html>` instead of `{`.  
**Fix:** Add browser-like headers, or use `lm-api-reads.fantasy.espn.com` as the domain.

```python
headers = {
    "Accept": "application/json",
    "Referer": "https://fantasy.espn.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."
}
```

### `kona_player_info` Without Filter Header

Requesting `kona_player_info` without an `X-Fantasy-Filter` header returns approximately 50 players with no guaranteed ordering. This is not documented by ESPN.

**Fix:** Always pass an explicit `X-Fantasy-Filter` header with a `limit` value when using this view.

### Combining Too Many Views

Requesting 6 or more `view` parameters in a single call can cause:
- Very high latency (10+ seconds)
- Occasional `400 Bad Request`
- Truncated or malformed responses in some sports

**Recommended:** Keep to 2–4 views per request. Parallelize if needed.

### `mTransactions2` Requires `scoringPeriodId`

The `mTransactions2` view scopes to a specific scoring period. Omitting `scoringPeriodId` may return an empty `transactions` array or only current-period transactions.

---

## Sport-Specific Gaps

### Fantasy Hockey (FHL)

- **Limited community documentation** — fewer open-source tools have been built for FHL vs FFL/FBA/FLB
- Lineup slot IDs and position IDs are not fully catalogued in community resources
- The `scoringPeriodId` cadence (daily) is the same as FBA and FLB, but stat category IDs are unique to hockey

### Fantasy Basketball (FBA)

- `kona_player_info` `filterSlotIds` values differ from football — position mapping not fully verified
- Roto vs category scoring formats behave differently; `cumulativeScore` object in matchups contains category win/loss data rather than point totals

### Fantasy Baseball (FLB)

- Lineup locking behavior per game (`INDIVIDUAL_GAME` locktime) creates complexity — a player's slot locks when their MLB game starts, not at a fixed time
- `stats` array in player entries uses a dense numeric key format (`"1": {"34": 182, "35": 78}`) where the outer key is a compound of `statTypeId` + `scoringPeriodId` + `seasonId`

---

## Fields That May Change

| Field | Known Issue |
|-------|-------------|
| `currentProjectedRank` in `teams[]` | Often returns `0` mid-season; not always a reliable standings indicator |
| `totalProjectedPointsLive` in matchups | Returns `0.0` before any games have started for the scoring period |
| `waiverProcessStatus` in `status` | Usually an empty object `{}`; contents documented nowhere |
| `pointsOverrides` in `scoringItems` | Always `{}` in most leagues; purpose unclear |
| `leagueRanking` / `leagueTotal` in `scoringItems` | Always `0`; appears to be unused legacy fields |
| `universeType` in `rosterSettings` | Always `0` in all observed responses |

---

## Authentication Pitfalls

### Cookie Expiry

`espn_s2` tokens are long-lived but not permanent. They expire or are invalidated by:
- Password changes
- Signing out of all devices
- ESPN-initiated session resets

Build in cookie refresh handling. Do not assume a previously-working `espn_s2` will still be valid.

### Username + Password Auth is Dead

ESPN previously supported a login endpoint at `registerdisney.go.com` that returned cookies programmatically. This approach was blocked when ESPN integrated Google reCAPTCHA into the login flow. It no longer works. The only viable auth method is manual cookie extraction from a browser session.

### SWID Format

`SWID` must include the surrounding curly braces in the cookie value:
```
SWID={A3EBBDAE-5F79-46FF-86EF-7356ABA27F8E}  ✅
SWID=A3EBBDAE-5F79-46FF-86EF-7356ABA27F8E    ❌
```

---

## Undocumented Behaviors

### Response is Array for Pre-2018 Seasons

When using the `leagueHistory` endpoint, the response is a JSON **array** containing a single league object, not a plain object. Parsing code must handle both formats.

### `mMatchup` vs `mMatchupScore`

Both views return schedule/matchup data, but they include slightly different fields. `mMatchup` is the older view name still present in some community code; `mMatchupScore` returns more complete scoring data. In practice, both work, but `mMatchupScore` is more reliable for getting point totals.

### `nominatingTeamId` in Auction Draft Picks

Auction draft picks include a `nominatingTeamId` field identifying which team put the player up for bid. This field is `null` or absent in snake draft picks. It is not documented and was discovered through source code analysis of the `espn-api` Python library.

### Players Endpoint is a Sub-Path

The player list endpoint (`players_wl` view) uses a `/players` sub-path, not the league-level endpoint:
```
GET https://lm-api-reads.fantasy.espn.com/apis/v3/games/{gameCode}/seasons/{seasonId}/players?view=players_wl
```
This is a different URL pattern from all other views.

### News Endpoint is Also a Sub-Path

Player news uses a completely different URL structure:
```
GET https://lm-api-reads.fantasy.espn.com/apis/v3/games/{gameCode}/news/players?playerId={id}
```

---

## Rate Limiting

ESPN does not publish rate limits for the Fantasy API. Community experience suggests:
- Rapid iteration over all scoring periods (e.g., 196 requests for a baseball season) may trigger temporary blocks
- Implement a minimum 100–500ms delay between requests when iterating
- Cache responses — league data does not change during off-hours

---

## Gaps / Unknowns

| Item | Status |
|------|--------|
| Full list of `statTypeId` values beyond 0–3 | UNVERIFIED |
| FHL lineup slot ID mapping | UNVERIFIED |
| FBA lineup slot ID mapping | PARTIALLY VERIFIED |
| `waiverProcessStatus` object contents | UNVERIFIED |
| Pagination behavior for `kona_player_info` without limit | PARTIALLY VERIFIED |
| Exact auth enforcement timeline for historical data | PARTIALLY VERIFIED |
| Whether `lm-api-reads` handles all views identically to `fantasy.espn.com` | PARTIALLY VERIFIED |
| Complete list of `filterStatus` values beyond the 4 documented | UNVERIFIED |
