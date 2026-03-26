# Response Schemas

This document describes the complete response objects returned by the ESPN Fantasy API, organized by data type. All schemas are derived from observed live responses.

> **Legend:**
> - **VERIFIED** — Directly observed from live API responses
> - **PARTIALLY VERIFIED** — Some evidence but not fully confirmed
> - **UNVERIFIED** — Likely exists based on pattern, not directly confirmed

---

## Top-Level League Response

All calls to the league endpoint return a top-level object. The fields present depend on which `view` parameters are requested.

```json
{
  "gameId": 2,
  "id": 101,
  "seasonId": 2025,
  "segmentId": 0,
  "scoringPeriodId": 196,
  "draftDetail": { ... },
  "members": [ ... ],
  "settings": { ... },
  "status": { ... },
  "teams": [ ... ],
  "schedule": [ ... ],
  "transactions": [ ... ],
  "players": [ ... ]
}
```

| Field | Present with view |
|-------|-------------------|
| `draftDetail` | `mDraftDetail` |
| `members` | `mTeam` |
| `settings` | `mSettings` |
| `status` | `mStatus`, `mSettings` |
| `teams` | `mTeam`, `mRoster` |
| `schedule` | `mMatchupScore`, `mStandings`, `mScoreboard` |
| `transactions` | `mTransactions2` |
| `players` | `kona_player_info` |

---

## Team Object (`teams[]`) — VERIFIED

```json
{
  "id": 1,
  "abbrev": "Card",
  "name": "St. Louis Cardinals",
  "divisionId": 1,
  "currentProjectedRank": 0,
  "owners": ["{A3EBBDAE-5F79-46FF-86EF-7356ABA27F8E}"],
  "record": {
    "overall": {
      "wins": 96,
      "losses": 239,
      "ties": 0,
      "percentage": 0.4636363636363636,
      "gamesBack": 0,
      "streakLength": 3,
      "streakType": "WIN"
    },
    "home": { "wins": 50, "losses": 118, ... },
    "away": { "wins": 46, "losses": 121, ... },
    "division": { "wins": 20, "losses": 40, ... }
  },
  "roster": {
    "entries": [ ... ]
  },
  "transactionCounter": {
    "acquisitions": 42,
    "drops": 40,
    "trades": 3,
    "moveToActive": 0,
    "moveToIR": 0
  }
}
```

---

## Member Object (`members[]`) — VERIFIED

```json
{
  "id": "{A3EBBDAE-5F79-46FF-86EF-7356ABA27F8E}",
  "displayName": "JohnDoe42",
  "firstName": "John",
  "lastName": "Doe",
  "isLeagueManager": false
}
```

---

## Roster Entry (`teams[].roster.entries[]`) — VERIFIED

```json
{
  "playerId": 4905919,
  "lineupSlotId": 0,
  "acquisitionDate": 1709863200000,
  "acquisitionType": "DRAFT",
  "injuryStatus": "ACTIVE",
  "playerPoolEntry": {
    "id": 4905919,
    "acquisitionDate": 1709863200000,
    "acquisitionType": "DRAFT",
    "percentOwned": 42.3,
    "percentStarted": 36.1,
    "totalPoints": 312.5,
    "appliedStatTotal": 312.5,
    "onTeamId": 1,
    "player": {
      "active": true,
      "defaultPositionId": 6,
      "droppable": true,
      "eligibleSlots": [4, 7, 12],
      "firstName": "Ezequiel",
      "fullName": "Ezequiel Tovar",
      "id": 4905919,
      "injured": false,
      "injuryStatus": "ACTIVE",
      "lastName": "Tovar",
      "proTeamId": 27
    }
  }
}
```

---

## Matchup Object (`schedule[]`) — VERIFIED

```json
{
  "id": 1,
  "matchupPeriodId": 1,
  "away": {
    "teamId": 1,
    "totalPoints": 847.5,
    "totalProjectedPointsLive": 847.5,
    "rosterForCurrentScoringPeriod": {
      "entries": [ ... ]
    },
    "cumulativeScore": {
      "loses": 3,
      "wins": 4,
      "statBySlot": null
    }
  },
  "home": {
    "teamId": 13,
    "totalPoints": 792.0,
    "totalProjectedPointsLive": 792.0,
    "rosterForCurrentScoringPeriod": {
      "entries": [ ... ]
    }
  },
  "playoffTierType": "NONE",
  "winner": "AWAY"
}
```

---

## Player Object (`players[]`) — VERIFIED

```json
{
  "id": 30417,
  "onTeamId": 0,
  "player": {
    "active": true,
    "defaultPositionId": 1,
    "droppable": true,
    "eligibleSlots": [13, 14, 15, 12],
    "firstName": "Fernando",
    "fullName": "Fernando Abad",
    "id": 30417,
    "injured": false,
    "injuryStatus": "ACTIVE",
    "lastName": "Abad",
    "proTeamId": 15,
    "ownership": {
      "averageDraftPosition": 260.0,
      "percentChange": -1.2,
      "percentOwned": 0.8,
      "percentStarted": 0.4
    }
  },
  "playerPoolEntry": {
    "acquisitionType": "DRAFT",
    "appliedStatTotal": 0.0,
    "keeperValue": 0,
    "keeperValueFuture": 0,
    "lineupLocked": false,
    "onTeamId": 0,
    "percentOwned": 0.8,
    "percentStarted": 0.4,
    "totalPoints": 0.0,
    "stats": [
      {
        "appliedStats": { "34": 182, "35": 78 },
        "appliedTotal": 0.0,
        "id": "0827002502024",
        "scoringPeriodId": 1,
        "seasonId": 2024,
        "statTypeId": 0
      }
    ]
  }
}
```

---

## Draft Pick Object (`draftDetail.picks[]`) — VERIFIED

```json
{
  "id": 1,
  "playerId": 42241,
  "overallPickNumber": 1,
  "roundId": 1,
  "roundPickNumber": 1,
  "teamId": 16,
  "bidAmount": 0,
  "autoDraftTypeId": 0,
  "tradeLocked": false,
  "keeper": false
}
```

---

## Transaction Object (`transactions[]`) — VERIFIED

```json
{
  "id": "af3512fe-0a45-43d2-a278-ea384f927032",
  "bidAmount": 1,
  "executionType": "WAIVER",
  "items": [
    { "fromTeamId": 0, "isKeeper": false, "overallPickNumber": 0, "playerId": 40026, "toTeamId": 16, "type": "ADD" },
    { "fromTeamId": 16, "isKeeper": false, "overallPickNumber": 0, "playerId": 41105, "toTeamId": 0, "type": "DROP" }
  ],
  "memberId": "{A3EBBDAE-5F79-46FF-86EF-7356ABA27F8E}",
  "priority": 3,
  "processDate": 1741060000000,
  "proposedDate": 1740955000000,
  "scoringPeriodId": 1,
  "status": "CANCELED",
  "teamId": 16,
  "type": "WAIVER"
}
```

---

## Status Object (`status`) — VERIFIED

```json
{
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
```

---

## Game Metadata Object (`/apis/v3/games/{code}`) — VERIFIED

```json
{
  "abbrev": "FLB",
  "active": true,
  "currentSeasonId": 2026,
  "name": "Fantasy Baseball",
  "proSportName": "baseball",
  "proSportAbbrev": "MLB"
}
```

---

## Error Objects

### 401 — Auth Required

```json
{
  "messages": ["You are not authorized to view this League."],
  "details": [
    {
      "message": "You are not authorized to view this League.",
      "shortMessage": "You are not authorized to view this League.",
      "type": "AUTH_LEAGUE_NOT_VISIBLE"
    }
  ]
}
```

### 404 — Not Found

```json
{
  "messages": ["Not Found"]
}
```

---

## Position and Slot ID Reference

### Football (FFL) — Default Position IDs

| `defaultPositionId` | Position |
|---------------------|----------|
| `1` | QB |
| `2` | RB |
| `3` | WR |
| `4` | TE |
| `5` | K |
| `16` | D/ST |

### Baseball (FLB) — Default Position IDs

| `defaultPositionId` | Position |
|---------------------|----------|
| `1` | SP |
| `2` | C |
| `3` | 1B |
| `4` | 2B |
| `5` | 3B |
| `6` | SS |
| `7` | LF |
| `8` | CF |
| `9` | RF |
| `10` | OF (generic) |
| `11` | DH |
| `12` | RP |

### Basketball (FBA) — Default Position IDs — PARTIALLY VERIFIED

| `defaultPositionId` | Position |
|---------------------|----------|
| `1` | PG |
| `2` | SG |
| `3` | SF |
| `4` | PF |
| `5` | C |

### Hockey (FHL) — Default Position IDs — PARTIALLY VERIFIED

| `defaultPositionId` | Position |
|---------------------|----------|
| `1` | C |
| `2` | LW |
| `3` | RW |
| `4` | D |
| `5` | G |

---

## Pro Team IDs — Baseball (FLB) — PARTIALLY VERIFIED

| `proTeamId` | Team |
|-------------|------|
| `27` | Colorado Rockies |
| `15` | Cincinnati Reds |
| `1` | Baltimore Orioles |
| `2` | Boston Red Sox |
| `3` | Chicago White Sox |
| `4` | Cleveland Guardians |
| `5` | Detroit Tigers |
| `6` | Houston Astros |
| `7` | Kansas City Royals |
| `8` | Los Angeles Angels |
| `9` | Minnesota Twins |
| `10` | New York Yankees |
| `11` | Oakland Athletics |
| `12` | Seattle Mariners |
| `13` | Texas Rangers |
| `14` | Toronto Blue Jays |
| `16` | Tampa Bay Rays |
| `17` | Chicago Cubs |
| `18` | Cincinnati Reds (alt) |
| `19` | Milwaukee Brewers |
| `20` | Pittsburgh Pirates |
| `21` | St. Louis Cardinals |
| `22` | Arizona Diamondbacks |
| `23` | Atlanta Braves |
| `24` | Los Angeles Dodgers |
| `25` | Miami Marlins |
| `26` | New York Mets |
| `28` | San Diego Padres |
| `29` | San Francisco Giants |
| `30` | Washington Nationals |
| `31` | Philadelphia Phillies |

> **Note:** `proTeamId: 0` typically indicates a free agent or no team assigned.
