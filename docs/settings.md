# Settings Reference

League settings are returned via the `mSettings` view. This document describes all fields in the `settings` object returned by the API.

---

## Acquisition Settings

**Object:** `settings.acquisitionSettings`

Controls how players are added and dropped from rosters.

| Field | Type | Description |
|-------|------|-------------|
| `acquisitionBudget` | integer | Total FAAB waiver budget per team |
| `acquisitionLimit` | integer | Max acquisitions per season (`-1` = unlimited) |
| `acquisitionType` | string | Waiver/FA system — see values below |
| `matchupAcquisitionLimit` | integer | Max adds per matchup period (`-1` = unlimited) |
| `minimumBid` | integer | Minimum FAAB bid amount |
| `waiverHours` | integer | Hours players remain on waivers before processing |
| `waiverOrderReset` | boolean | Whether waiver order resets after each claim |
| `waiverProcessHour` | integer | Hour of day (0–23) when waivers process |

**Acquisition type values:**

| Value | Description |
|-------|-------------|
| `WAIVERS_TRADITIONAL` | Traditional rolling waiver order |
| `WAIVERS_CONTINUOUS` | Continuous waivers (FAAB-based bidding) |
| `FREE_AGENT` | No waivers — immediate adds allowed |

---

## Draft Settings

**Object:** `settings.draftSettings`

| Field | Type | Description |
|-------|------|-------------|
| `auctionBudget` | integer | Starting auction budget per team |
| `availableDate` | integer | Unix ms timestamp when the draft becomes available |
| `date` | integer | Unix ms timestamp of scheduled draft start |
| `isTradingEnabled` | boolean | Whether draft pick trading is enabled |
| `keeperCount` | integer | Number of keeper players allowed |
| `keeperCountFuture` | integer | Keeper count for future seasons |
| `keeperOrderType` | string | `TRADITIONAL`, `AUCTION` |
| `leagueSubType` | string | `FULL_DRAFT`, `AUCTION`, `KEEPER` |
| `pickOrder` | array[integer] | Manual draft order (array of team IDs) |
| `timePerSelection` | integer | Seconds per pick |
| `type` | string | `SNAKE`, `AUCTION`, `OFFLINE` |

**Draft type values:**

| Value | Description |
|-------|-------------|
| `SNAKE` | Traditional snake draft |
| `AUCTION` | Live auction draft |
| `LINEAR` | Non-snake (same order every round) |
| `OFFLINE` | Draft not conducted on ESPN platform |

---

## Finance Settings

**Object:** `settings.financeSettings`

| Field | Type | Description |
|-------|------|-------------|
| `entryFee` | float | League entry fee |
| `miscFee` | float | Miscellaneous fee |
| `perLoss` | float | Fee per loss |
| `perTrade` | float | Fee per trade |
| `playerAcquisitionBudget` | float | Total acquisition fee budget |
| `playerAcquisitionType` | string | `NONE`, `AUCTION` |

---

## Roster Settings

**Object:** `settings.rosterSettings`

| Field | Type | Description |
|-------|------|-------------|
| `lineupLocktimeType` | string | When lineup lock occurs — see below |
| `lineupSlotCounts` | object | Map of slot ID → count |
| `moveLimit` | integer | Max roster moves per season (`-1` = unlimited) |
| `positionLimits` | object | Map of position ID → max per roster |
| `universeType` | integer | Player universe: `0` = standard, `1` = old |

**Lineup lock type values:**

| Value | Description |
|-------|-------------|
| `INDIVIDUAL_GAME` | Locks when a player's game starts |
| `SCORING_PERIOD` | Locks at the start of the scoring period |

---

## Schedule Settings

**Object:** `settings.scheduleSettings`

| Field | Type | Description |
|-------|------|-------------|
| `divisions[]` | array | Divisions in the league |
| `divisions[].id` | integer | Division ID (0-indexed) |
| `divisions[].name` | string | Division name |
| `divisions[].size` | integer | Number of teams in division |
| `matchupPeriodCount` | integer | Total number of regular season matchup periods |
| `matchupPeriodLength` | integer | Number of scoring periods per matchup |
| `matchupPeriods` | object | Map of matchup period → scoring period IDs |
| `playoffMatchupPeriodLength` | integer | Length of each playoff matchup period |
| `playoffSeedingRule` | string | How playoff seeds are determined |
| `playoffSeedingRuleBy` | integer | Tiebreaker rule ID |
| `playoffTeamCount` | integer | Number of teams that make playoffs |

**Playoff seeding rule values:**

| Value | Description |
|-------|-------------|
| `TOTAL_POINTS_SCORED` | Seeded by cumulative points scored |
| `H2H_RECORD` | Seeded by head-to-head record |
| `WINNING_PCT` | Seeded by winning percentage |

---

## Scoring Settings

**Object:** `settings.scoringSettings`

| Field | Type | Description |
|-------|------|-------------|
| `playerRankType` | string | Default ranking type used: `STANDARD`, `PPR`, `HALF_PPR` |
| `scoringItems[]` | array | Scoring rules — one per stat category |
| `scoringType` | string | League scoring format |

**`scoringItems[]` fields:**

| Field | Type | Description |
|-------|------|-------------|
| `statId` | integer | Stat category ID (sport-specific) |
| `points` | float | Fantasy points per occurrence |
| `isReverseItem` | boolean | `true` = lower stat = more points (e.g., ERA) |
| `leagueRanking` | float | Unused (always 0) |
| `leagueTotal` | float | Unused (always 0) |

---

## Trade Settings

**Object:** `settings.tradeSettings`

| Field | Type | Description |
|-------|------|-------------|
| `allowOutOfUniverse` | boolean | Whether out-of-universe players can be traded |
| `deadlineDate` | integer | Trade deadline (Unix ms; `0` = no deadline) |
| `maxNegotiationDays` | integer | Days a trade offer remains open |
| `revisionHours` | integer | Hours to revise a trade after acceptance before it executes |
| `vetoType` | string | How trades are vetoed |
| `vetoVotesRequired` | integer | Votes required to veto (when `vetoType = OWNER_VOTE`) |

**Veto type values:**

| Value | Description |
|-------|-------------|
| `OWNER_VOTE` | League managers vote to veto |
| `LEAGUE_MANAGER` | Only the league manager can veto |
| `NONE` | No veto system |

---

## League-Level Fields

These fields are returned at the top level alongside `settings`:

| Field | Type | Description |
|-------|------|-------------|
| `gameId` | integer | ESPN game ID (`1` = FFL, `2` = FLB, `3` = FBA, `5` = FHL) |
| `id` | integer | League ID |
| `seasonId` | integer | Season year |
| `segmentId` | integer | Segment (0 = full season) |
| `scoringPeriodId` | integer | Current scoring period |
| `settings.isPublic` | boolean | Whether the league is publicly viewable |
| `settings.isCustomizable` | boolean | Whether settings are customizable mid-season |
| `settings.isAutoReactivate` | boolean | Whether injured reserve auto-reactivates |
| `settings.restrictionType` | string | `NONE`, `FOR_FRIENDS_ONLY` |

### ESPN Game IDs

| `gameId` | Game |
|----------|------|
| `1` | Fantasy Football (FFL) |
| `2` | Fantasy Baseball (FLB) |
| `3` | Fantasy Basketball (FBA) |
| `5` | Fantasy Hockey (FHL) |

---

## Notes

- **VERIFIED:** All fields above are directly observed from live API responses for public FLB League 101, season 2025.
- **PARTIALLY VERIFIED:** Some FFL, FBA, and FHL-specific fields may include additional entries not present in FLB responses (e.g., defensive scoring items in FFL).
- The `matchupPeriods` map in `scheduleSettings` contains the exact scoring period IDs for each matchup, which is the source of truth for building calendar views.
