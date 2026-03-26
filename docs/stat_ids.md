# Stat Category IDs

ESPN Fantasy uses numeric stat category IDs to key all statistical data in responses from `kona_player_info`, `mBoxscore`, and player `stats[]` arrays. This document catalogs the known IDs for each sport.

> **Important:** Stat IDs are sport-specific. A stat ID of `1` means "passing attempts" in football but "at-bats" in baseball. Never mix stat IDs across sports.

---

## How Stat IDs Appear in Responses

Within `playerPoolEntry.stats[].appliedStats`:
```json
{
  "appliedStats": {
    "1": 580,
    "3": 4230,
    "4": 39,
    "20": 5
  },
  "appliedTotal": 312.5,
  "scoringPeriodId": 1,
  "statTypeId": 0
}
```

The outer keys (`"1"`, `"3"`, `"4"`, `"20"`) are the stat category IDs. The values are the raw stat amounts (yards, touchdowns, etc.).

The points each stat is worth is configured in `settings.scoringSettings.scoringItems[].statId`.

---

## Fantasy Football (FFL) — Stat IDs — PARTIALLY VERIFIED

### Passing
| Stat ID | Description |
|---------|-------------|
| `1` | Passing attempts |
| `2` | Passing completions |
| `3` | Passing yards |
| `4` | Passing touchdowns |
| `20` | Interceptions thrown |
| `19` | Fumbles lost |
| `23` | 2-point conversions (passing) |

### Rushing
| Stat ID | Description |
|---------|-------------|
| `24` | Rushing attempts |
| `25` | Rushing yards |
| `26` | Rushing touchdowns |
| `27` | 2-point conversions (rushing) |

### Receiving
| Stat ID | Description |
|---------|-------------|
| `42` | Receptions |
| `43` | Receiving yards |
| `44` | Receiving touchdowns |
| `45` | 2-point conversions (receiving) |

### Kicking
| Stat ID | Description |
|---------|-------------|
| `74` | FG made 0–19 yards |
| `75` | FG made 20–29 yards |
| `76` | FG made 30–39 yards |
| `77` | FG made 40–49 yards |
| `78` | FG made 50+ yards |
| `79` | FG missed (any distance) |
| `80` | PAT made |
| `81` | PAT missed |

### Defense / Special Teams (D/ST)
| Stat ID | Description |
|---------|-------------|
| `89` | Sacks |
| `90` | Interceptions (defensive) |
| `91` | Fumble recoveries |
| `93` | Defensive touchdowns |
| `95` | Safeties |
| `96` | Blocked kicks |
| `97` | Kick return touchdowns |
| `98` | Punt return touchdowns |
| `99` | Interception return touchdowns |
| `120` | Points allowed (ranges determine points: 0 pts = max, 35+ = penalty) |

> **Note:** Defensive stat scoring uses ranges. The `scoringItems` for D/ST contain `pointsOverrides` entries that map point-ranges to point values.

---

## Fantasy Baseball (FLB) — Stat IDs — PARTIALLY VERIFIED

### Batting
| Stat ID | Description |
|---------|-------------|
| `1` | At-bats |
| `2` | Hits |
| `3` | Doubles |
| `4` | Triples |
| `5` | Home runs |
| `6` | Runs scored |
| `7` | RBI |
| `8` | Walks |
| `9` | Hit by pitch |
| `10` | Strikeouts (batting) |
| `11` | Stolen bases |
| `12` | Caught stealing |
| `13` | Batting average (derived) |
| `17` | Slugging percentage (derived) |
| `18` | On-base percentage (derived) |

### Pitching
| Stat ID | Description |
|---------|-------------|
| `32` | Innings pitched |
| `34` | Strikeouts (pitching) |
| `35` | Wins |
| `36` | Losses |
| `37` | Saves |
| `38` | Earned runs |
| `39` | Hits allowed |
| `40` | Walks allowed |
| `41` | Hit batters |
| `42` | ERA (derived) |
| `43` | WHIP (derived) |
| `48` | Holds |
| `53` | Quality starts |
| `63` | Blown saves |

---

## Fantasy Basketball (FBA) — Stat IDs — PARTIALLY VERIFIED

| Stat ID | Description |
|---------|-------------|
| `0` | Points |
| `1` | Blocks |
| `2` | Steals |
| `3` | Assists |
| `4` | Offensive rebounds |
| `5` | Defensive rebounds |
| `6` | Total rebounds (`4` + `5`) |
| `11` | Turnovers |
| `13` | Field goals made |
| `14` | Field goals attempted |
| `15` | Field goal % (derived) |
| `17` | Free throws made |
| `18` | Free throws attempted |
| `19` | Free throw % (derived) |
| `21` | 3-pointers made |
| `40` | Minutes played |
| `42` | Double-doubles |
| `43` | Triple-doubles |

---

## Fantasy Hockey (FHL) — Stat IDs — UNVERIFIED

| Stat ID | Description (estimated) |
|---------|------------------------|
| `1` | Goals |
| `2` | Assists |
| `3` | Points (`1` + `2`) |
| `4` | Plus/minus |
| `5` | Penalty minutes |
| `6` | Power play points |
| `7` | Shots on goal |
| `8` | Short-handed points |
| `14` | Wins (goalie) |
| `15` | Goals against average (goalie) |
| `16` | Save percentage (goalie) |
| `17` | Saves |
| `19` | Shutouts |

> **UNVERIFIED:** Hockey stat IDs have not been confirmed against live API responses. Use as a starting point only; verify against a real FHL league's `scoringSettings.scoringItems`.

---

## Retrieving Your League's Stat IDs

The authoritative source for stat IDs in your specific league is the `scoringSettings.scoringItems` array from `mSettings`:

```bash
curl "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=mSettings"
```

Each `scoringItem` maps `statId` → `points`:
```json
{
  "scoringItems": [
    { "statId": 3, "points": 0.04, "isReverseItem": false },
    { "statId": 4, "points": 4.0, "isReverseItem": false },
    { "statId": 20, "points": -2.0, "isReverseItem": true }
  ]
}
```

This gives you the exact stat IDs that generate scoring for your league's rules.
