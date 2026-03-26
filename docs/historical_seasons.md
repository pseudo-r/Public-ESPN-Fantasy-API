# Historical Seasons

This document covers how to access data from past ESPN Fantasy seasons, including the alternate endpoint used for seasons before 2018.

---

## Overview

ESPN Fantasy API stores historical league data for all seasons a league has been active. Accessing that data requires using the correct endpoint pattern, which changed in 2018.

> **⚠️ Auth restriction (August 2025):** As of August 1, 2025, ESPN restricted access to historical season data for many leagues. Requesting historical data without `espn_s2` authentication now returns a 401 even for leagues that were previously public. Always use cookies when accessing historical seasons.

---

## Endpoint Patterns by Season

### 2018 and Later — VERIFIED

```
GET https://lm-api-reads.fantasy.espn.com/apis/v3/games/{gameCode}/seasons/{seasonId}/segments/0/leagues/{leagueId}
```

This is identical to the `fantasy.espn.com` endpoint, just routed through the internal read domain. All `view` parameters work normally.

### 2017 and Earlier — PARTIALLY VERIFIED

```
GET https://lm-api-reads.fantasy.espn.com/apis/v3/games/{gameCode}/leagueHistory/{leagueId}?seasonId={year}
```

| Difference | Detail |
|------------|--------|
| Path structure | Uses `leagueHistory/{leagueId}` instead of `seasons/{year}/segments/0/leagues/{leagueId}` |
| Response format | Returns an **array** with a single league object, not a plain object |
| Data richness | Pre-2018 data has less granularity — final rosters and scores only, limited intra-season data |
| Auth requirement | Requires `espn_s2` and `SWID` cookies in almost all cases |

**Example:**
```bash
# 2017 Fantasy Football season for a league
curl "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/leagueHistory/336358?seasonId=2017" \
  --cookie "espn_s2=YOUR_S2; SWID=YOUR_SWID"
```

**Response format (pre-2018):**
```json
[
  {
    "id": 336358,
    "seasonId": 2017,
    "teams": [ ... ],
    "schedule": [ ... ],
    "draftDetail": { ... }
  }
]
```

> The response is wrapped in an array. Always access `response[0]` when parsing pre-2018 data.

---

## Hybrid Fetch Strategy

When building tools that need to support both historical and current seasons, implement endpoint fallback logic:

```python
import requests

def get_league_data(game_code, league_id, year, espn_s2=None, swid=None, view="mSettings"):
    cookies = {}
    if espn_s2 and swid:
        cookies = {"espn_s2": espn_s2, "SWID": swid}

    base = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/{game_code}"

    # Try the modern endpoint first
    if year >= 2018:
        url = f"{base}/seasons/{year}/segments/0/leagues/{league_id}"
    else:
        url = f"{base}/leagueHistory/{league_id}?seasonId={year}"

    r = requests.get(url, params={"view": view}, cookies=cookies)

    if r.status_code == 401:
        # ESPN may have flipped the endpoint it responds to — try the other format
        if "leagueHistory" in url:
            url = f"{base}/seasons/{year}/segments/0/leagues/{league_id}"
        else:
            url = f"{base}/leagueHistory/{league_id}?seasonId={year}"
        r = requests.get(url, params={"view": view}, cookies=cookies)

    data = r.json()
    # Pre-2018 wraps in array
    return data[0] if isinstance(data, list) else data
```

---

## `previousSeasons` Field

When fetching `mStatus` for any league, the `status.previousSeasons` field lists all past season years for that league:

```json
{
  "status": {
    "previousSeasons": [2024, 2023, 2022, 2021]
  }
}
```

Use this field to discover which historical seasons are available for a given league before querying them.

---

## Domain Notes

ESPN uses two equivalent domains for fantasy API access:

| Domain | Notes |
|--------|-------|
| `fantasy.espn.com` | Public-facing domain; same API, works for browser requests |
| `lm-api-reads.fantasy.espn.com` | Internal read subdomain; discovered April 2024; same endpoints, same responses |

Both domains return identical data. `lm-api-reads` is used internally by the ESPN Fantasy web app. Some clients target this domain directly because it avoids occasional bot-detection redirects from `fantasy.espn.com`.

---

## Season ID Reference

| Sport | Season notation | Example |
|-------|----------------|---------|
| Football | Year the season starts | `2024` = 2024–25 NFL season |
| Baseball | Calendar year | `2025` = 2025 MLB season |
| Basketball | Year the season ends | `2025` = 2024–25 NBA season |
| Hockey | Year the season ends | `2025` = 2024–25 NHL season |

> **PARTIALLY VERIFIED:** Basketball and hockey season ID conventions are based on community reports. Confirm against `currentSeasonId` from the game metadata endpoint before building season-scoped tools.

---

## Known Historical Data Gaps

- **Pre-2018 only provides final state** — you cannot query individual scoring periods or weekly rosters for seasons before 2018
- **Draft data before 2018** may be incomplete or unavailable
- **Transaction history** is generally not available for pre-2018 seasons
- **Auth requirement as of Aug 2025:** Historical data that was previously accessible without cookies may now require authentication even for historically-public leagues
