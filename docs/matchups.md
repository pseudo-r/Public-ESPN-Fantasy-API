# Matchups & Scoring

Matchup and scoring data is accessed through the main league endpoint using the `mMatchupScore`, `mBoxscore`, and `mScoreboard` views. Scoring periods and matchup periods are distinct concepts that must both be understood to correctly query live and historical scoring data.

---

## Concepts: Scoring Periods vs. Matchup Periods

| Term | Description |
|------|-------------|
| **Scoring Period** (`scoringPeriodId`) | A single real-world time interval. In football: 1 week. In baseball/basketball/hockey: 1 day. |
| **Matchup Period** (`matchupPeriodId`) | A group of scoring periods that form one head-to-head matchup. In football, this usually equals one week. In daily sports, a matchup typically spans 7 days = 7 scoring periods. |
| **Segment** | A block of the season (regular season = segment 0, playoffs = segments 1–3). |

**Relationship for fantasy football:**
- Week 1 = matchup period 1 = scoring periods 1–7 (or period 1 only, with line locks per game)

**Relationship for fantasy baseball:**
- Matchup period 1 = scoring periods 1–7 (first week of games)
- Each day within that matchup is a separate `scoringPeriodId`

---

## Matchup Schedule: `mMatchupScore`

Returns the full schedule with scores.

```
GET https://fantasy.espn.com/apis/v3/games/{gameCode}/seasons/{seasonId}/segments/0/leagues/{leagueId}?view=mMatchupScore&matchupPeriodId={n}
```

**`schedule[]` matchup object:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique matchup identifier |
| `matchupPeriodId` | integer | Which matchup period |
| `away.teamId` | integer | Away team ID |
| `away.totalPoints` | float | Away team points |
| `away.totalProjectedPointsLive` | float | Live projected finish for away team |
| `away.cumulativeScore` | object | Cumulative stats for roto/category leagues |
| `home.teamId` | integer | Home team ID |
| `home.totalPoints` | float | Home team points |
| `home.totalProjectedPointsLive` | float | Live projected finish for home team |
| `home.cumulativeScore` | object | Cumulative stats for roto/category leagues |
| `winner` | string | `HOME`, `AWAY`, `UNDECIDED`, `NONE_YET` |
| `playoffTierType` | string | `NONE`, `WINNERS_BRACKET`, `LOSERS_BRACKET`, `CONSOLATION` |

**Retrieving all matchups for a season:**

Omit `matchupPeriodId` to get all matchups:
```bash
curl "https://fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=mMatchupScore"
```

---

## Boxscore: `mBoxscore`

Returns per-player scoring entries for a specific matchup. This is the most detailed scoring endpoint.

```
GET https://fantasy.espn.com/apis/v3/games/{gameCode}/seasons/{seasonId}/segments/0/leagues/{leagueId}?view=mBoxscore&matchupPeriodId={n}&scoringPeriodId={n}
```

**`schedule[].home.rosterForCurrentScoringPeriod.entries[]` fields:**

| Field | Type | Description |
|-------|------|-------------|
| `playerId` | integer | ESPN player ID |
| `lineupSlotId` | integer | Active lineup slot |
| `playerPoolEntry.appliedStatTotal` | float | Total fantasy points scored by this player |
| `playerPoolEntry.stats[]` | array | Detailed stat breakdown (one entry per scoring period) |
| `playerPoolEntry.player.fullName` | string | Player name |
| `playerPoolEntry.player.proTeamId` | integer | Pro team |

---

## Scoreboard: `mScoreboard`

Alias for current-week scoreboard. Equivalent to `mMatchupScore` for the current active matchup period, without needing to specify the period ID manually.

```bash
# Current week scoreboard
GET https://fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=mScoreboard
```

---

## Scoring Types

ESPN Fantasy supports multiple scoring formats. The league's scoring type is returned in `settings.scoringSettings.scoringType`:

| Value | Description |
|-------|-------------|
| `H2H_POINTS` | Head-to-head points (most common in football) |
| `H2H_CATEGORY` | Head-to-head categories (most common in basketball/hockey) |
| `ROTO` | Rotisserie scoring (ranks across all teams) |
| `POINTS` | Total points (no head-to-head) |

---

## Scoring Items

Each scoring item in `settings.scoringSettings.scoringItems[]` defines how many points a given stat earns:

| Field | Type | Description |
|-------|------|-------------|
| `statId` | integer | ESPN internal stat category ID |
| `points` | float | Points per occurrence of this stat |
| `isReverseItem` | boolean | Whether lower = better (e.g., turnovers) |
| `pointsOverrides` | object | Team-specific point overrides if applicable |

---

## Sport-Specific Scoring Period Behavior

| Sport | `scoringPeriodId` = 1 | Typical matchup length |
|-------|----------------------|------------------------|
| Football (FFL) | Week 1 of the regular season | 1 scoring period = 1 week |
| Basketball (FBA) | Day 1 of the regular season | ~7 scoring periods per matchup |
| Baseball (FLB) | Day 1 of the season | ~7 scoring periods per matchup |
| Hockey (FHL) | Day 1 of the season | ~7 scoring periods per matchup |

**Baseball scoring period cadence:**
- Opening Day = `scoringPeriodId: 1`
- Day 196 of the season ≈ `scoringPeriodId: 196` (verified from live FLB league 101, 2025)

---

## Example: Full Week 1 Boxscore Fetch (Football)

```bash
# Get full boxscore for matchup period 1
curl "https://fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=mBoxscore&matchupPeriodId=1&scoringPeriodId=1" \
  --cookie "espn_s2=YOUR_S2; SWID=YOUR_SWID"
```

## Example: Baseball Weekly Matchup

```bash
# Get matchup period 1 scores (baseball, first week)
curl "https://fantasy.espn.com/apis/v3/games/flb/seasons/2025/segments/0/leagues/101?view=mMatchupScore&matchupPeriodId=1"
```

---

## Playoffs

Playoff matchups are still served through the same `mMatchupScore` and `mBoxscore` views. The `playoffTierType` field distinguishes them:

| Value | Description |
|-------|-------------|
| `NONE` | Regular season matchup |
| `WINNERS_BRACKET` | Playoff bracket matchup |
| `LOSERS_BRACKET` | Consolation bracket matchup |
| `CONSOLATION` | Consolation round |
| `TOILET_BOWL` | Last-place bracket (some leagues) |

---

## Live Scoring

During active games, `totalProjectedPointsLive` on each matchup side updates in near-real-time as the ESPN Fantasy system processes live game data. This field is `0.0` or absent before games begin.

> **PARTIALLY VERIFIED:** Live update frequency is not officially documented. Observed cadence is approximately 60 seconds during active scoring periods.
