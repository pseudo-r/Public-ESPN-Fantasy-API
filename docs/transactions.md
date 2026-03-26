# Transactions & Waivers

Transactions are recorded in the league's activity log and returned through the `mTransactions2` view. This includes waiver claims, free agent adds, drops, and trades.

---

## Endpoint

```
GET https://fantasy.espn.com/apis/v3/games/{gameCode}/seasons/{seasonId}/segments/0/leagues/{leagueId}?view=mTransactions2&scoringPeriodId={n}
```

The `scoringPeriodId` parameter is required to scope transactions to a specific period. To retrieve all transactions across the season, iterate over all valid scoring periods.

---

## Response Structure

**Top-level key:** `transactions`

**`transactions[]` fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | UUID of the transaction |
| `type` | string | Transaction type — see values below |
| `status` | string | Current transaction status |
| `teamId` | integer | Team that initiated the transaction |
| `scoringPeriodId` | integer | Scoring period when the transaction was processed |
| `processDate` | integer | Unix ms timestamp of processing |
| `proposedDate` | integer | Unix ms timestamp of when proposed |
| `bidAmount` | integer | FAAB bid amount (0 for non-FAAB waiver claims) |
| `priority` | integer | Waiver priority position (lower = higher priority) |
| `items[]` | array | Players involved in the transaction |
| `executionType` | string | `BASIC`, `WAIVER`, `TRADE` |

---

## Transaction Types

| Value | Description |
|-------|-------------|
| `WAIVER` | Player claimed from waivers |
| `FREE_AGENT` | Player added from free agency |
| `TRADE` | Trade between two teams |
| `DRAFT` | Initial draft pick (appears in some views) |
| `AUCTION` | Auction draft acquisition |

---

## Transaction Status Values

| Value | Description |
|-------|-------------|
| `EXECUTED` | Transaction has been completed |
| `CANCELED` | Transaction was canceled by the team manager |
| `PENDING` | Waiver claim pending processing |
| `VETOED` | Trade was vetoed by the league |
| `FAILED` | Transaction failed (insufficient FAAB or waiver logic error) |

---

## Items Array (`items[]`)

Each transaction contains one or more `items` representing individual player movements:

| Field | Type | Description |
|-------|------|-------------|
| `playerId` | integer | ESPN player ID |
| `type` | string | `ADD` or `DROP` |
| `fromTeamId` | integer | Source team ID (trades and drops; `0` if from free agency) |
| `toTeamId` | integer | Destination team ID (adds and trades; `0` if dropped to FA pool) |

---

## Sample Transactions

**Waiver Claim (Canceled):**
```json
{
  "id": "af3512fe-0a45-43d2-a278-ea384f927032",
  "status": "CANCELED",
  "teamId": 16,
  "type": "WAIVER",
  "scoringPeriodId": 1,
  "processDate": 1741060000000,
  "bidAmount": 1,
  "priority": 3,
  "items": [
    { "playerId": 40026, "type": "ADD", "fromTeamId": 0, "toTeamId": 16 },
    { "playerId": 41105, "type": "DROP", "fromTeamId": 16, "toTeamId": 0 }
  ]
}
```

**Trade (Executed):**
```json
{
  "id": "b2c3d4e5-...",
  "status": "EXECUTED",
  "teamId": 3,
  "type": "TRADE",
  "scoringPeriodId": 10,
  "processDate": 1741200000000,
  "bidAmount": 0,
  "items": [
    { "playerId": 4430807, "type": "ADD", "fromTeamId": 7, "toTeamId": 3 },
    { "playerId": 4241985, "type": "DROP", "fromTeamId": 3, "toTeamId": 7 }
  ]
}
```

**Free Agent Add:**
```json
{
  "id": "c3d4e5f6-...",
  "status": "EXECUTED",
  "teamId": 5,
  "type": "FREE_AGENT",
  "scoringPeriodId": 5,
  "processDate": 1739000000000,
  "bidAmount": 0,
  "items": [
    { "playerId": 42100, "type": "ADD", "fromTeamId": 0, "toTeamId": 5 }
  ]
}
```

---

## Waiver System Details

The waiver behavior is configured in `settings.acquisitionSettings`:

| Setting | Impact |
|---------|--------|
| `acquisitionType: "WAIVERS_TRADITIONAL"` | Rolling waiver priority order; claims reset order |
| `acquisitionType: "WAIVERS_CONTINUOUS"` | FAAB bidding; `bidAmount` represents the FAAB bid |
| `waiverHours: 24` | Players sit on waivers for 24 hours before processed |
| `waiverProcessHour: 3` | Waivers process at 3 AM league time |

---

## Retrieving Full Season Transactions

The `mTransactions2` view scopes to a specific `scoringPeriodId`. To retrieve all transactions for a season:

```javascript
const leagueUrl = `https://fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/${leagueId}`;

// First get status to find scoring period range
const statusResp = await fetch(`${leagueUrl}?view=mStatus`, {credentials: 'include'});
const {status} = await statusResp.json();

const {firstScoringPeriod, latestScoringPeriod} = status;
const allTransactions = [];

for (let period = firstScoringPeriod; period <= latestScoringPeriod; period++) {
  const resp = await fetch(`${leagueUrl}?view=mTransactions2&scoringPeriodId=${period}`, {credentials: 'include'});
  const data = await resp.json();
  if (data.transactions) {
    allTransactions.push(...data.transactions);
  }
}
```

> **Note:** Iterating over all scoring periods generates many requests. Implement caching and rate limiting.

---

## Notes

- **VERIFIED:** Transaction structure confirmed from live FLB League 101 (public, season 2025). UUIDs, status codes, and items structure are accurate.
- **PARTIALLY VERIFIED:** Trade-specific fields (`fromTeamId`, `toTeamId` in multi-player trades) may contain additional nested metadata not captured in this documentation.
- FAAB `bidAmount` is present but `0` for non-FAAB leagues. There is no separate field to distinguish FAAB from non-FAAB waiver priorities.
