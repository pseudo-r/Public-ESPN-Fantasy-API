# League Endpoints

All league data is accessed through a single parameterized endpoint, filtered using the `view` query parameter. This document covers every known view and its behavior.

---

## Endpoint Pattern

```
GET https://fantasy.espn.com/apis/v3/games/{gameCode}/seasons/{seasonId}/segments/0/leagues/{leagueId}
```

### Path Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `gameCode` | ✅ | `ffl` (football), `fba` (basketball), `flb` (baseball), `fhl` (hockey) |
| `seasonId` | ✅ | Four-digit season year (e.g., `2025`) |
| `leagueId` | ✅ | Numeric league ID found in the URL on fantasy.espn.com |

> Use `segments/0` for all standard requests. Other segment values correspond to playoff rounds and are rarely needed.

---

## View: `mSettings`

Returns the full league configuration including scoring rules, roster slot definitions, draft settings, acquisition rules, and trade settings.

**Request:**
```bash
GET https://fantasy.espn.com/apis/v3/games/flb/seasons/2025/segments/0/leagues/101?view=mSettings
```

**Top-level response keys:** `draftDetail`, `gameId`, `id`, `scoringPeriodId`, `seasonId`, `segmentId`, `settings`, `status`

**`settings` object keys:** `acquisitionSettings`, `draftSettings`, `financeSettings`, `isAutoReactivate`, `isCustomizable`, `isPublic`, `name`, `restrictionType`, `rosterSettings`, `scheduleSettings`, `scoringSettings`, `size`, `tradeSettings`

**Sample response (abbreviated):**
```json
{
  "draftDetail": { "drafted": true, "inProgress": false },
  "gameId": 2,
  "id": 101,
  "scoringPeriodId": 196,
  "seasonId": 2025,
  "segmentId": 0,
  "settings": {
    "name": "My League Name",
    "size": 12,
    "isPublic": true,
    "isCustomizable": false,
    "restrictionType": "NONE",
    "acquisitionSettings": {
      "acquisitionBudget": 100,
      "acquisitionLimit": -1,
      "acquisitionType": "WAIVERS_TRADITIONAL",
      "matchupAcquisitionLimit": -1,
      "minimumBid": 1,
      "waiverHours": 24,
      "waiverOrderReset": true,
      "waiverProcessHour": 3
    },
    "draftSettings": {
      "auctionBudget": 260,
      "availableDate": 1709863200000,
      "date": 0,
      "isTradingEnabled": false,
      "keeperCount": 0,
      "keeperCountFuture": 0,
      "keeperOrderType": "TRADITIONAL",
      "leagueSubType": "FULL_DRAFT",
      "pickOrder": [],
      "timePerSelection": 90,
      "type": "OFFLINE"
    },
    "rosterSettings": {
      "lineupLocktimeType": "INDIVIDUAL_GAME",
      "lineupSlotCounts": {
        "0": 1,
        "1": 1,
        "2": 2,
        "3": 1,
        "4": 3,
        "5": 1,
        "7": 3,
        "12": 5,
        "13": 0,
        "14": 0,
        "15": 0,
        "16": 0,
        "17": 5,
        "21": 0
      },
      "moveLimit": -1,
      "positionLimits": { "1": 14, "2": 10, "3": 10, "4": 10, "5": 10, "7": 10 },
      "universeType": 0
    },
    "scoringSettings": {
      "matchupPeriods": {},
      "playerRankType": "STANDARD",
      "scoringItems": [
        { "isReverseItem": false, "leagueRanking": 0, "leagueTotal": 0, "points": 1, "statId": 1, "pointsOverrides": {} }
      ],
      "scoringType": "ROTO"
    },
    "scheduleSettings": {
      "divisions": [ { "id": 0, "name": "Division 1", "size": 6 } ],
      "matchupPeriodCount": 26,
      "matchupPeriodLength": 7,
      "matchupPeriods": { "1": [1,2,3,4,5,6,7] },
      "playoffMatchupPeriodLength": 7,
      "playoffSeedingRule": "TOTAL_POINTS_SCORED",
      "playoffSeedingRuleBy": 0,
      "playoffTeamCount": 4
    },
    "tradeSettings": {
      "allowOutOfUniverse": false,
      "deadlineDate": 0,
      "maxNegotiationDays": 7,
      "revisionHours": 24,
      "vetoVotesRequired": 4,
      "vetoType": "OWNER_VOTE"
    }
  },
  "status": {
    "activatedDate": 1709863200000,
    "createdAsLMLeague": false,
    "currentMatchupPeriod": 26,
    "finalScoringPeriod": 196,
    "firstScoringPeriod": 1,
    "isActive": true,
    "isExpired": false,
    "isFull": true,
    "isPlayoffMatchupEdited": false,
    "isToBeDeleted": false,
    "isViewable": true,
    "isWaiverOrderEdited": false,
    "latestScoringPeriod": 196,
    "previousSeasons": [2024, 2023],
    "standingsUpdateDate": 0,
    "teamsJoined": 16,
    "transactionScoringPeriod": 196,
    "waiverLastExecutionDate": 1741060000000,
    "waiverProcessStatus": {}
  }
}
```

---

## View: `mTeam`

Returns all teams in the league with owner information, division placement, and season record.

**Request:**
```bash
GET https://fantasy.espn.com/apis/v3/games/flb/seasons/2025/segments/0/leagues/101?view=mTeam
```

**Top-level response keys:** `draftDetail`, `gameId`, `id`, `members`, `scoringPeriodId`, `seasonId`, `segmentId`, `status`, `teams`

**`teams[]` object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Team ID within the league |
| `abbrev` | string | Team abbreviation |
| `name` | string | Full team name |
| `divisionId` | integer | Division ID (0-indexed) |
| `owners` | array[string] | Array of owner SWID GUIDs |
| `currentProjectedRank` | integer | Current projected final standing |
| `record.overall` | object | `wins`, `losses`, `ties`, `percentage` |
| `record.home` | object | Home record |
| `record.away` | object | Away record |
| `record.division` | object | In-division record |

**`members[]` object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Member SWID |
| `displayName` | string | Display name |
| `firstName` | string | First name |
| `lastName` | string | Last name |

**Sample `teams[0]`:**
```json
{
  "abbrev": "Card",
  "currentProjectedRank": 0,
  "divisionId": 1,
  "id": 1,
  "name": "St. Louis Cardinals",
  "owners": ["{A3EBBDAE-5F79-46FF-86EF-7356ABA27F8E}"],
  "record": {
    "overall": {
      "losses": 239,
      "percentage": 0.4636363636363636,
      "wins": 96
    }
  }
}
```

---

## View: `mRoster`

Returns current roster entries for all teams. Requires `scoringPeriodId` to specify the week or day.

**Request:**
```bash
GET https://fantasy.espn.com/apis/v3/games/flb/seasons/2025/segments/0/leagues/101?view=mRoster&scoringPeriodId=1
```

**`teams[].roster.entries[]` object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `playerId` | integer | ESPN player ID |
| `lineupSlotId` | integer | Current lineup slot (see lineup slot ID table) |
| `acquisitionDate` | integer | Unix timestamp (ms) of acquisition |
| `acquisitionType` | string | `DRAFT`, `WAIVER`, `FREE_AGENT`, `TRADE` |
| `playerPoolEntry.id` | integer | Same as `playerId` |
| `playerPoolEntry.player.fullName` | string | Player full name |
| `playerPoolEntry.player.proTeamId` | integer | Pro team ID |
| `playerPoolEntry.player.defaultPositionId` | integer | Default position ID |

**Sample `teams[0].roster.entries[0]`:**
```json
{
  "playerId": 4905919,
  "lineupSlotId": 0,
  "acquisitionDate": 1709863200000,
  "acquisitionType": "DRAFT",
  "playerPoolEntry": {
    "id": 4905919,
    "player": {
      "fullName": "Ezequiel Tovar",
      "proTeamId": 27,
      "defaultPositionId": 6
    }
  }
}
```

### Lineup Slot IDs

Lineup slot IDs differ by sport. The following are common values:

**Fantasy Football (`ffl`):**

| Slot ID | Position |
|---------|----------|
| `0` | QB |
| `2` | RB |
| `4` | WR |
| `6` | TE |
| `16` | D/ST |
| `17` | K |
| `20` | Bench |
| `21` | IR |
| `23` | FLEX |

**Fantasy Baseball (`flb`):**

| Slot ID | Position |
|---------|----------|
| `0` | C |
| `1` | 1B |
| `2` | 2B |
| `3` | 3B |
| `4` | SS |
| `5` | OF |
| `7` | Util |
| `12` | Bench |
| `13` | SP |
| `14` | RP |
| `15` | P |
| `17` | P (starting pitcher slot) |

---

## View: `mMatchupScore`

Returns the schedule and scores for a specific matchup period.

**Request:**
```bash
GET https://fantasy.espn.com/apis/v3/games/flb/seasons/2025/segments/0/leagues/101?view=mMatchupScore&matchupPeriodId=1
```

**Top-level response keys include:** `schedule`

**`schedule[]` object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Matchup ID |
| `matchupPeriodId` | integer | Which matchup period |
| `away.teamId` | integer | Away team ID |
| `away.totalPoints` | float | Away team total points |
| `home.teamId` | integer | Home team ID |
| `home.totalPoints` | float | Home team total points |
| `winner` | string | `HOME`, `AWAY`, `UNDECIDED` |
| `playoffTierType` | string | `NONE`, `WINNERS_BRACKET`, `LOSERS_BRACKET` |

**Sample `schedule[0]`:**
```json
{
  "away": { "teamId": 1, "totalPoints": 0 },
  "home": { "teamId": 13, "totalPoints": 0 },
  "id": 1,
  "matchupPeriodId": 1,
  "winner": "AWAY"
}
```

---

## View: `mStandings`

Returns the same `schedule` array as `mMatchupScore` but is optimized for standings calculations. Cumulative records are embedded within each team object in `mTeam`.

**Request:**
```bash
GET https://fantasy.espn.com/apis/v3/games/flb/seasons/2025/segments/0/leagues/101?view=mStandings
```

---

## View: `mStatus`

Returns high-level league lifecycle status. Useful for determining whether the draft has occurred, whether the league is in playoffs, and key period IDs.

**Request:**
```bash
GET https://fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=mStatus
```

**`status` object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `activatedDate` | integer | Unix ms timestamp of league activation |
| `currentMatchupPeriod` | integer | Current active matchup period |
| `firstScoringPeriod` | integer | First scoring period ID of the season |
| `finalScoringPeriod` | integer | Last scoring period ID of the season |
| `latestScoringPeriod` | integer | Most recently completed scoring period |
| `isActive` | boolean | Whether the league is currently active |
| `isFull` | boolean | Whether the league has reached capacity |
| `isExpired` | boolean | Whether the season has ended |
| `isViewable` | boolean | Whether the league is publicly viewable |
| `teamsJoined` | integer | Number of teams that have joined |
| `previousSeasons` | array[integer] | List of prior season years this league existed |
| `waiverLastExecutionDate` | integer | Unix ms timestamp of last waiver processing |

---

## View: `mDraftDetail`

Returns the complete draft history for the league.

**Request:**
```bash
GET https://fantasy.espn.com/apis/v3/games/flb/seasons/2025/segments/0/leagues/101?view=mDraftDetail
```

**`draftDetail` object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `drafted` | boolean | Whether the draft has occurred |
| `inProgress` | boolean | Whether the draft is currently in progress |
| `completeDate` | integer | Unix ms timestamp when draft completed |
| `picks[]` | array | List of draft pick objects |

**`picks[]` object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Pick ID |
| `playerId` | integer | ESPN player ID |
| `teamId` | integer | Team ID that made the pick |
| `overallPickNumber` | integer | Overall pick position (1-based) |
| `roundId` | integer | Round number |
| `roundPickNumber` | integer | Pick number within the round |
| `bidAmount` | integer | Auction bid amount (0 for snake drafts) |
| `autoDraftTypeId` | integer | `0` = manual, `1` = auto-drafted |
| `tradeLocked` | boolean | Whether the player is trade-locked post-draft |

**Sample `draftDetail`:**
```json
{
  "completeDate": 1741057401675,
  "drafted": true,
  "inProgress": false,
  "picks": [
    {
      "id": 1,
      "playerId": 42241,
      "overallPickNumber": 1,
      "roundId": 1,
      "roundPickNumber": 1,
      "teamId": 16,
      "bidAmount": 0,
      "autoDraftTypeId": 0,
      "tradeLocked": false
    }
  ]
}
```

---

## View: `mTransactions2`

Returns all activity log entries for the league. Requires `scoringPeriodId`.

**Request:**
```bash
GET https://fantasy.espn.com/apis/v3/games/flb/seasons/2025/segments/0/leagues/101?view=mTransactions2&scoringPeriodId=1
```

**`transactions[]` object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | UUID of the transaction |
| `status` | string | `EXECUTED`, `CANCELED`, `PENDING`, `VETOED` |
| `type` | string | `WAIVER`, `FREE_AGENT`, `TRADE`, `DRAFT` |
| `teamId` | integer | Team initiating the transaction |
| `scoringPeriodId` | integer | Scoring period when the transaction occurred |
| `processDate` | integer | Unix ms timestamp |
| `bidAmount` | integer | Waiver bid amount (FAAB systems) |
| `items[]` | array | Players added/dropped in this transaction |

**`items[]` object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `playerId` | integer | ESPN player ID |
| `type` | string | `ADD`, `DROP` |
| `fromTeamId` | integer | Source team (for trades) |
| `toTeamId` | integer | Destination team (for trades) |

**Sample `transactions[0]`:**
```json
{
  "id": "af3512fe-0a45-43d2-a278-ea384f927032",
  "status": "CANCELED",
  "teamId": 16,
  "type": "WAIVER",
  "scoringPeriodId": 1,
  "processDate": 1741060000000,
  "bidAmount": 1,
  "items": [
    { "playerId": 40026, "type": "ADD", "toTeamId": 16 },
    { "playerId": 41105, "type": "DROP", "fromTeamId": 16 }
  ]
}
```

---

## View: `mBoxscore`

Returns detailed per-player scoring breakdown for a specific matchup. Useful for building a boxscore view.

**Request:**
```bash
GET https://fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=mBoxscore&matchupPeriodId=1&scoringPeriodId=1
```

**`schedule[].home` and `schedule[].away` object fields (in boxscore context):**

| Field | Type | Description |
|-------|------|-------------|
| `teamId` | integer | Team ID |
| `totalPoints` | float | Total points scored |
| `totalProjectedPointsLive` | float | Live projected final points |
| `rosterForCurrentScoringPeriod.entries[]` | array | Player entries with scoring |
| `rosterForCurrentScoringPeriod.entries[].playerPoolEntry.appliedStatTotal` | float | Points scored by this player |

---

## Combining Multiple Views

Multiple views can be requested in a single API call. This reduces round trips significantly.

```bash
# Teams + Rosters + Standings in one call
GET https://fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=mTeam&view=mRoster&view=mMatchupScore&scoringPeriodId=1&matchupPeriodId=1
```

> **Note:** Very large combined requests (e.g., all 10+ views simultaneously) may result in high latency or timeouts. Prefer grouping 2–4 views per request.

---

## View: `proTeamSchedules_wl`

Returns the schedule for NFL/NBA/MLB/NHL professional teams. Used by fantasy apps to determine bye weeks and upcoming matchups.

**Request:**
```bash
GET https://fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=proTeamSchedules_wl
```

**Response key:** `proTeamSchedules`

---

## View: `mScoreboard`

An alias for scoreboard data. Returns the current scoring period and schedule data. Functionally similar to `mMatchupScore` but defaults to the current scoring period without requiring `matchupPeriodId`.

**Request:**
```bash
GET https://fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=mScoreboard
```

---

## View: `mMatchup`

An older view name that returns matchup data. Functionally overlaps with `mMatchupScore`. Returns the `schedule` array including each matchup's team IDs, scores, and roster associations.

> **Note:** Some community code uses `mMatchup` interchangeably with `mMatchupScore`. Both work, but `mMatchupScore` is the recommended name as of 2019+.

**Request:**
```bash
GET https://fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=mMatchup&matchupPeriodId=1
```

---

## View: `mPositionalRatings` — PARTIALLY VERIFIED

Returns positional strength-of-schedule ratings by opponent. This shows how each team's defense ranks against each position, used for start/sit decisions.

**Request:**
```bash
GET https://fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=mPositionalRatings&scoringPeriodId=1
```

**Response key:** `positionAgainstOpponent.positionalRatings`

**`positionalRatings` structure:**
```json
{
  "positionAgainstOpponent": {
    "positionalRatings": {
      "QB": {
        "ratingsByOpponent": {
          "1": { "rank": 3, "totalPointsAgainst": 312.5 },
          "2": { "rank": 18, "totalPointsAgainst": 198.2 }
        }
      }
    }
  }
}
```

Where the outer key is a position abbreviation and the `ratingsByOpponent` keys are Pro team IDs.

---

## View: `kona_playercard` — PARTIALLY VERIFIED

Returns detailed player pool entry data for a specific set of player IDs. More focused than `kona_player_info` — used when you need deep stats for individual players.

**Requires `X-Fantasy-Filter` header with `filterIds`.**

**Request:**
```bash
curl "https://fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=kona_playercard" \
  -H 'X-Fantasy-Filter: {"players":{"filterIds":{"value":[3054211,3895342]},"filterStatsForTopScoringPeriodIds":{"value":5,"additionalValue":["002025","102025"]}}}'
```

**`X-Fantasy-Filter` fields for `kona_playercard`:**

| Filter field | Type | Description |
|--------------|------|-------------|
| `filterIds.value` | array[integer] | Player IDs to fetch |
| `filterStatsForTopScoringPeriodIds.value` | integer | Number of top scoring periods to include |
| `filterStatsForTopScoringPeriodIds.additionalValue` | array[string] | Season/type codes (e.g., `"002025"` = season 2025, type 0) |

---

## View: `kona_league_messageboard` — PARTIALLY VERIFIED

Returns league message board threads. Uses a different sub-path and optionally filters by message type.

**Sub-path:** `/communication` appended after the game code and season
```
GET https://lm-api-reads.fantasy.espn.com/apis/v3/games/{gameCode}/seasons/{seasonId}/segments/0/leagues/{leagueId}/communication?view=kona_league_messageboard
```

**Optionally filter by message type using `X-Fantasy-Filter`:**
```json
{
  "topicsByType": {
    "ACTIVITY_NOTIFICATIONS": {
      "sortMessageDate": { "sortPriority": 1, "sortAsc": false }
    }
  }
}
```

**Common message types:**

| Value | Description |
|-------|-------------|
| `ACTIVITY_NOTIFICATIONS` | Transaction and activity notifications |
| `CHAT` | League chat messages |
| `TRADE_NOTIFICATIONS` | Trade offer notifications |
| `WAIVER_NOTIFICATIONS` | Waiver claim notifications |

---

## Sub-Path Endpoints

These endpoints use a different URL pattern from the main league endpoint.

### Player List (`players_wl`)

Returns all active professional players for a sport/season. Used to map player IDs to names.

```
GET https://lm-api-reads.fantasy.espn.com/apis/v3/games/{gameCode}/seasons/{seasonId}/players?view=players_wl
```

**Required header:**
```json
X-Fantasy-Filter: {"filterActive": {"value": true}}
```

**Response:** Array of player objects with `id` and `fullName`.

```json
[
  { "id": 3054211, "fullName": "Patrick Mahomes", "proTeamId": 12 },
  { "id": 3895342, "fullName": "Josh Allen", "proTeamId": 2 }
]
```

### Player News

Returns news articles for a specific player by ESPN player ID.

```
GET https://lm-api-reads.fantasy.espn.com/apis/v3/games/{gameCode}/news/players?playerId={playerId}
```

**Response:** Array of news items for the player (injury updates, news blurbs, beat reporter notes).

---

## View: `mLiveScoring` — VERIFIED

Returns real-time live scoring updates during an active week. When combined with `mBoxscore` and `mScoreboard`, it returns each team's active roster, current total projected points, and live points per player — with two stat objects per roster entry: original projections and live actuals.

**Request:**
```bash
GET https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=mLiveScoring&scoringPeriodId={currentPeriod}
```

**Best used with:**
```bash
?view=mBoxscore&view=mLiveScoring&view=mScoreboard&scoringPeriodId={currentPeriod}
```

**Key response fields (within `schedule[].home` / `schedule[].away`):**

| Field | Type | Description |
|-------|------|-------------|
| `totalPoints` | float | Current live total |
| `totalProjectedPointsLive` | float | Projected final total |
| `rosterForCurrentScoringPeriod.entries[]` | array | Per-player entries with 2 stat objects each |
| `entries[].playerPoolEntry.appliedStatTotal` | float | Live points from this player |

> **Note:** `mLiveScoring` data is only meaningful during an active scoring period. Outside of game days it returns the same data as `mMatchupScore`.

---

## View: `mSchedule` — VERIFIED

Returns the full season schedule for all teams in the league. Each entry in the `schedule` array includes team IDs, matchup period, and score data.

**Request:**
```bash
GET https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=mSchedule
```

**Response key:** `schedule` array (same structure as `mMatchupScore`, without live point data)

**Difference from `mMatchupScore`:** `mSchedule` returns all matchups for the season without requiring a `matchupPeriodId` filter. Useful for rendering a full-season schedule view.

---

## View: `mStandings` — VERIFIED

Returns team standings including overall record, divisional record, and points data. Used as part of the initial league fetch in the espn-api library alongside `mTeam`, `mRoster`, `mMatchup`, and `mSettings`.

**Request:**
```bash
GET https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=mStandings
```

**Response key:** `teams[]` — each team includes:

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Team ID |
| `record.overall.wins` | integer | Total wins |
| `record.overall.losses` | integer | Total losses |
| `record.overall.ties` | integer | Total ties |
| `record.overall.pointsFor` | float | Total points scored |
| `record.overall.pointsAgainst` | float | Total points against |
| `rankCalculatedFinal` | integer | Final standing rank |
| `divisionStanding` | integer | Rank within division |

> **Tip:** `mTeam` also includes standings data. Use `mStandings` when you only need the standings object and want a lighter response.

---

## View: `modular` — PARTIALLY VERIFIED

A meta-view that can return various "module" blocks of data depending on the current application state. Primarily used by the ESPN Fantasy website itself for rendering dynamic page sections. The exact modules returned depend on the context and are not consistently documented.

**Request:**
```bash
GET https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb/seasons/2025/segments/0/leagues/{leagueId}?view=mPositionalRatings&view=mSettings&view=mTeam&view=modular&view=mNav
```

> **Note:** `modular` and `mNav` are typically used together by the Fantasy website. For programmatic access, prefer explicit views like `mTeam`, `mSettings`, and `mMatchupScore` rather than relying on `modular`.

---

## Complete View Reference

| View | Primary Response Key | Auth Required | Notes |
|------|---------------------|---------------|-------|
| `mSettings` | `settings` | Public | Full league config |
| `mTeam` | `teams[]` | Public | Teams + records + owners |
| `mRoster` | `teams[].roster` | Public | Rosters for scoring period |
| `mMatchupScore` | `schedule[]` | Public | Points per matchup |
| `mMatchup` | `schedule[]` | Public | Alias for mMatchupScore |
| `mBoxscore` | `schedule[]` | Public | Per-player scoring breakdown |
| `mLiveScoring` | `schedule[]` | Public | Real-time live point totals |
| `mScoreboard` | `schedule[]` | Public | Current period scoreboard |
| `mSchedule` | `schedule[]` | Public | Full season schedule |
| `mStandings` | `teams[]` | Public | Season standings/records |
| `mStatus` | `status` | Public | Scoring period, season state |
| `mDraftDetail` | `draftDetail` | Private* | Draft picks |
| `mTransactions2` | `transactions[]` | Private* | Waiver/trade/FA activity |
| `mPositionalRatings` | `positionAgainstOpponent` | Public | Defensive SOS ratings |
| `kona_player_info` | `players[]` | Public | Filtered player pool |
| `kona_playercard` | `players[]` | Public | Per-player deep stats |
| `kona_league_messageboard` | `topics` | Private* | League message board |
| `players_wl` | array | Public | All active pro players |
| `proTeamSchedules_wl` | `proTeamSchedules` | Public | Pro team schedules |
| `modular` | varies | Public | ESPN website modules |
| `mNav` | varies | Public | Website nav state |

*Private: Requires `espn_s2` and `SWID` cookies for private leagues or historical data
