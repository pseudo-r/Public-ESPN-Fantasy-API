---
name: "🐛 Bug Report"
about: "Report a broken or incorrect ESPN Fantasy API endpoint or response"
title: "[BUG] "
labels: ["bug"]
assignees: []
---

## Endpoint / View

<!-- The full URL and view parameter(s) you used -->
```
GET https://lm-api-reads.fantasy.espn.com/apis/v3/games/{gameCode}/seasons/{seasonId}/segments/0/leagues/{leagueId}?view=
```

## Expected Behavior

<!-- What did you expect to get back? -->

## Actual Behavior

<!-- What did you actually get? Include status code and JSON snippet -->

**Status code:**
**Response:**
```json

```

## Steps to Reproduce

```bash
curl -H "Cookie: espn_s2=...; SWID=..." \
  "https://lm-api-reads.fantasy.espn.com/..."
```

## Environment

- Date tested:
- Game code (ffl/fba/flb/fhl):
- Season:
- League visibility (public/private):
