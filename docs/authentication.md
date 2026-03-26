# Authentication

The ESPN Fantasy API supports both public and private league access. Authentication uses browser session cookies rather than API keys.

---

## Public Leagues

Leagues with the "Publicly Viewable" setting enabled in their league settings are accessible without any authentication. All views work on public leagues with standard GET requests.

**Verification:** VERIFIED — confirmed that publicly-configured ESPN Fantasy Baseball League 101 (2025 season) returns full JSON with no cookies required.

---

## Private Leagues

Private leagues require two cookies sent with every request. These cookies are obtained by logging in to `fantasy.espn.com` through a browser session.

### Required Cookies

| Cookie | Type | Description |
|--------|------|-------------|
| `espn_s2` | string | Long-lived session token (~200+ alphanumeric characters) |
| `SWID` | string | ESPN user GUID, enclosed in curly braces. Format: `{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}` |

### How to Find Your Cookies

**Method 1: Browser DevTools**
1. Log in at `https://fantasy.espn.com`
2. Open DevTools: `F12` or right-click → Inspect
3. Navigate to **Application → Storage → Cookies → https://fantasy.espn.com**
4. Copy the values for `espn_s2` and `SWID`

**Method 2: Browser Network Tab**
1. Log in at `https://fantasy.espn.com`
2. Open DevTools → **Network** tab
3. Navigate to your league
4. Click any request to `fantasy.espn.com` or `lm-api-reads.fantasy.espn.com`
5. In **Request Headers**, find the `Cookie` header
6. Extract `espn_s2=...` and `SWID=...`

### Sending Cookies in Requests

**curl:**
```bash
curl "https://fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=mSettings" \
  --cookie "espn_s2=YOUR_ESPN_S2_TOKEN; SWID={YOUR-SWID-GUID}"
```

**Python (requests):**
```python
import requests

cookies = {
    "espn_s2": "YOUR_ESPN_S2_TOKEN",
    "SWID": "{YOUR-SWID-GUID}"
}

url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/YOUR_LEAGUE_ID"
r = requests.get(url, params={"view": "mSettings"}, cookies=cookies)
data = r.json()
```

**JavaScript (fetch with credentials):**
```javascript
// When called from within fantasy.espn.com context, credentials are sent automatically
const response = await fetch(
  "https://fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/YOUR_LEAGUE_ID?view=mSettings",
  { credentials: "include" }
);
const data = await response.json();
```

---

## Authentication Error Responses

### 401 — Unauthorized (Private League, No Auth)

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

**Status code:** `401`  
**Error type:** `AUTH_LEAGUE_NOT_VISIBLE`

This response is returned when:
- A private league is requested without valid `espn_s2` and `SWID` cookies
- The authenticated user is not a member of the requested private league

### 404 — Not Found

```json
{
  "messages": ["Not Found"]
}
```

Returned when the `leagueId` does not exist in the requested `seasonId`, or the league was never created for that season.

---

## Important Security Notes

- **Never commit your `espn_s2` token** to version control. It grants full access to your ESPN account.
- **Tokens rotate.** The `espn_s2` cookie has a long TTL but may be invalidated by password changes or session expiries. Expect to re-fetch cookies periodically.
- **SWID is semi-permanent.** The `SWID` is your ESPN user ID and changes rarely or never.
- **No OAuth.** ESPN does not offer an official OAuth flow for the Fantasy API. Cookie-based auth is the only supported method.

---

## Public vs. Private Data Access

| Data Type | Public League | Private League |
|-----------|:---:|:---:|
| League settings (`mSettings`) | ✅ | ✅ (with auth) |
| Team data (`mTeam`) | ✅ | ✅ (with auth) |
| Rosters (`mRoster`) | ✅ | ✅ (with auth) |
| Draft picks (`mDraftDetail`) | ✅ | ✅ (with auth) |
| Standings (`mStandings`) | ✅ | ✅ (with auth) |
| Matchup scores (`mMatchupScore`) | ✅ | ✅ (with auth) |
| Transactions (`mTransactions2`) | ✅ | ✅ (with auth) |
| Player pool (`kona_player_info`) | ✅ | ✅ (with auth) |
| Game metadata (`/games/{code}`) | ✅ | N/A (no auth needed) |
