# Draft Endpoints

Draft data is accessed through the `mDraftDetail` view on the main league endpoint. This view returns the complete draft history for a league season, regardless of whether the draft was conducted live on ESPN, via auction, or offline.

---

## Endpoint

```
GET https://fantasy.espn.com/apis/v3/games/{gameCode}/seasons/{seasonId}/segments/0/leagues/{leagueId}?view=mDraftDetail
```

No additional query parameters are required. The full draft history is returned immediately.

---

## Response Structure

**Top-level key returned:** `draftDetail`

**`draftDetail` object:**

| Field | Type | Description |
|-------|------|-------------|
| `drafted` | boolean | `true` if the draft has occurred |
| `inProgress` | boolean | `true` during an active live draft |
| `completeDate` | integer | Unix ms timestamp when the draft completed |
| `picks[]` | array | All draft picks in order |

---

## Pick Object (`picks[]`)

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Sequential pick identifier (1-based) |
| `playerId` | integer | ESPN player ID of the drafted player |
| `teamId` | integer | Team ID that made the pick |
| `overallPickNumber` | integer | Overall draft position (1 = first pick overall) |
| `roundId` | integer | Round number (1-based) |
| `roundPickNumber` | integer | Pick number within the round |
| `bidAmount` | integer | Auction bid amount (0 for snake drafts) |
| `autoDraftTypeId` | integer | `0` = manual pick, `1` = auto-drafted |
| `tradeLocked` | boolean | Whether this player is trade-locked based on draft rules |
| `keeper` | boolean | `true` if this player was a keeper (not a fresh pick) |

---

## Sample Response

```json
{
  "draftDetail": {
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
        "tradeLocked": false,
        "keeper": false
      },
      {
        "id": 2,
        "playerId": 40026,
        "overallPickNumber": 2,
        "roundId": 1,
        "roundPickNumber": 2,
        "teamId": 4,
        "bidAmount": 0,
        "autoDraftTypeId": 0,
        "tradeLocked": false,
        "keeper": false
      }
    ]
  }
}
```

---

## Live Draft State

During a live draft (`inProgress: true`), the `picks[]` array reflects picks as they are made. Polling this endpoint during a draft gives real-time pick updates.

**Recommended polling interval:** 10–30 seconds during an active draft.

---

## Draft Types

The draft type is configured in `settings.draftSettings.type` (returned via `mSettings`). The data structure in `mDraftDetail` is the same regardless of draft type, but behavior differs:

| Type | `bidAmount` | `overallPickNumber` |
|------|-------------|---------------------|
| `SNAKE` | Always `0` | Sequential 1, 2, 3... |
| `AUCTION` | Dollar amount won | Order bids were finalized |
| `OFFLINE` | `0` | Order entered manually |

---

## Resolving Player Names from Draft Data

Draft picks only contain `playerId`. To resolve player names:

1. Fetch `view=kona_player_info` to get the full player pool
2. Map `playerId` → `player.fullName`

```javascript
const draftResp = await fetch(`...?view=mDraftDetail`, {credentials: 'include'});
const {draftDetail} = await draftResp.json();

const playerResp = await fetch(`...?view=kona_player_info`, {credentials: 'include'});
const {players} = await playerResp.json();

const playerMap = Object.fromEntries(players.map(p => [p.id, p.player.fullName]));

const picksWithNames = draftDetail.picks.map(pick => ({
  ...pick,
  playerName: playerMap[pick.playerId] ?? `Player #${pick.playerId}`
}));
```

---

## Keeper Leagues

In keeper leagues (`settings.draftSettings.keeperCount > 0`), picks with `keeper: true` reflect pre-draft keeper designations, not live auction or snake picks. These picks appear at the start of the picks array.

---

## Notes

- **VERIFIED:** Full draft history confirmed from live FLB League 101 (public, season 2025). The `completeDate`, `picks[]`, and all pick fields are accurate.
- **PARTIALLY VERIFIED:** `autoDraftTypeId` values beyond `0` and `1` are not fully mapped.
- **UNVERIFIED:** The behavior of `tradeLocked` for keeper leagues where draft picks are traded is not fully documented.
