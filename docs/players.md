# Players & Projections

Player data in the ESPN Fantasy API is provided through the `kona_player_info` view. This endpoint returns the full player pool for a given sport and league context, with optional filters for availability status, position, and ranking.

---

## Player Pool Endpoint

```
GET https://fantasy.espn.com/apis/v3/games/{gameCode}/seasons/{seasonId}/segments/0/leagues/{leagueId}?view=kona_player_info
```

**Optional query parameters:**
- `scoringPeriodId` — The current scoring period (week/day)

**Required for filtering:** Pass the `X-Fantasy-Filter` header as a JSON string.

---

## X-Fantasy-Filter Header

The `X-Fantasy-Filter` header controls what subset of players is returned. Without it, the API returns the full player pool (can be thousands of players).

**Header name:** `X-Fantasy-Filter`  
**Header value:** JSON string

### Filter Structure

```json
{
  "players": {
    "filterStatus": {
      "value": ["FREEAGENT", "WAIVERS"]
    },
    "filterSlotIds": {
      "value": [0, 2, 4, 6, 17, 16]
    },
    "filterRanksForScoringPeriodIds": {
      "value": [1]
    },
    "limit": 50,
    "offset": 0,
    "sortPercOwned": {
      "sortPriority": 1,
      "sortAsc": false
    }
  }
}
```

### Filter Fields

| Field | Type | Description |
|-------|------|-------------|
| `filterStatus.value` | array[string] | Player availability status — see values below |
| `filterSlotIds.value` | array[integer] | Filter by lineup slot / position |
| `filterRanksForScoringPeriodIds.value` | array[integer] | Scoring periods to rank rankings against |
| `limit` | integer | Max players to return (default varies) |
| `offset` | integer | Pagination offset |
| `sortPercOwned.sortPriority` | integer | Sort priority (lower = higher priority) |
| `sortPercOwned.sortAsc` | boolean | `false` = descending (most owned first) |

### Player Status Values

| Value | Description |
|-------|-------------|
| `FREEAGENT` | Player is a free agent (immediately claimable) |
| `WAIVERS` | Player is on waivers |
| `ONTEAM` | Player is rostered by a team |
| `INJURED_RESERVE` | Player is on a team but on IR |

---

## Free Agent Request Example

```bash
# Get top 50 free agents for Fantasy Football (QBs, RBs, WRs, TEs)
curl "https://fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=kona_player_info&scoringPeriodId=1" \
  -H 'X-Fantasy-Filter: {"players":{"filterStatus":{"value":["FREEAGENT","WAIVERS"]},"filterSlotIds":{"value":[0,2,4,6]},"limit":50,"sortPercOwned":{"sortPriority":1,"sortAsc":false}}}' \
  --cookie "espn_s2=YOUR_S2; SWID=YOUR_SWID"
```

---

## Response Structure

**Top-level keys:** `players`

**`players[]` object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | ESPN player ID |
| `onTeamId` | integer | Team ID if rostered, else `0` |
| `player` | object | Player metadata |
| `playerPoolEntry` | object | Pool data (ownership, acquisition info) |
| `ratings` | object | ESPN positional ratings |

**`player` object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `fullName` | string | Player full name |
| `firstName` | string | First name |
| `lastName` | string | Last name |
| `active` | boolean | Whether the player is active |
| `proTeamId` | integer | Current pro team ID |
| `defaultPositionId` | integer | Primary position ID |
| `eligibleSlots` | array[integer] | Lineup slots this player can fill |
| `injuryStatus` | string | `ACTIVE`, `QUESTIONABLE`, `DOUBTFUL`, `OUT`, `INJURY_RESERVE`, `SUSPENDED` |

**`playerPoolEntry` object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `acquisitionDate` | integer | Unix ms timestamp of last acquisition |
| `acquisitionType` | string | How this player was acquired |
| `percentOwned` | float | Ownership percentage across all leagues |
| `percentStarted` | float | Start percentage across all leagues |
| `totalPoints` | float | Season total fantasy points |
| `appliedStatTotal` | float | Points applied for current scoring period |
| `stats` | array | Statistical entries (see below) |
| `ownership` | object | Ownership and ADP data |

**`ownership` object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `averageDraftPosition` | float | ADP across recent ESPN drafts |
| `percentOwned` | float | Roster ownership % |
| `percentStarted` | float | Start % |

---

## Sample Player Object

```json
{
  "id": 30417,
  "onTeamId": 0,
  "player": {
    "active": true,
    "fullName": "Fernando Abad",
    "defaultPositionId": 1,
    "proTeamId": 15,
    "eligibleSlots": [13, 14, 15, 12],
    "injuryStatus": "ACTIVE"
  },
  "playerPoolEntry": {
    "acquisitionType": "DRAFT",
    "percentOwned": 12.4,
    "percentStarted": 8.1,
    "totalPoints": 42.5,
    "ownership": {
      "averageDraftPosition": 260,
      "percentOwned": 12.4,
      "percentStarted": 8.1
    }
  }
}
```

---

## Player Statistics (`stats[]`)

Each player object may contain a `stats` array. Statistics are keyed by `statTypeId` and `scoringPeriodId` combinations.

**`stats[]` object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `appliedStats` | object | Keyed by stat category ID → value |
| `appliedTotal` | float | Total fantasy points for this stat entry |
| `scoringPeriodId` | integer | Scoring period this entry corresponds to |
| `statTypeId` | integer | Type: `0` = actual, `1` = projected |
| `seasonId` | integer | Season year |

**Stat type IDs:**

| Value | Meaning |
|-------|---------|
| `0` | Actual season stats |
| `1` | Projected stats (remainder of season) |
| `2` | Projected stats (week-level) |
| `3` | Projected stats (today/next game) |

> Stat category IDs are sport-specific and correspond to ESPN's internal stat category system (e.g., passing yards, rushing TDs, etc.). These IDs are documented in the [Settings Reference](settings.md).

---

## Projections

Projections are included in the player pool data as `stats` entries with `statTypeId: 1` (season projection) or `statTypeId: 2` (weekly projection).

Projected fantasy points are available in `appliedTotal` on matching stat entries.

**Example — finding a player's weekly projection:**
```javascript
const player = data.players[0];
const weeklyProjection = player.playerPoolEntry.stats.find(
  s => s.statTypeId === 1 && s.scoringPeriodId === currentScoringPeriodId
);
const projectedPoints = weeklyProjection?.appliedTotal ?? 0;
```

---

## Rankings

Player rankings are embedded in the player pool entry. The rank object contains:

| Field | Type | Description |
|-------|------|-------------|
| `rank` | integer | Overall rank |
| `rankType` | string | `PPR`, `STANDARD`, `HALF_PPR` (football) |
| `auctionValue` | float | Projected auction dollar value |

> Rankings are only available when `filterRanksForScoringPeriodIds` is set in the filter header.

---

## Notes & Limitations

- **Large datasets:** Without a filter, `kona_player_info` can return thousands of players. Always use `X-Fantasy-Filter` with a `limit` in production.
- **PARTIALLY VERIFIED:** The full list of `statTypeId` values beyond 0 and 1 has not been fully confirmed for all sports.
- **Sport differences:** Position slot IDs and stat category IDs differ significantly across FFL, FBA, FLB, and FHL. Consult the per-sport slot IDs in [docs/leagues.md](leagues.md).
