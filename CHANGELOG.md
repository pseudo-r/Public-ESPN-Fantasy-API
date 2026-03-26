# CHANGELOG

All notable documentation changes to this project are recorded here.

## [1.0.0] — 2026-03-26

### Initial Release

Complete initial documentation for the ESPN Fantasy API (all four sports):

#### Documentation Structure
- Added `README.md` — Overview, quick start, game codes, segments, endpoint catalog, and query parameters reference
- Added `docs/authentication.md` — Cookie-based auth model, espn_s2/SWID guide, public vs. private access
- Added `docs/leagues.md` — All view parameters with verified schemas and sample responses
- Added `docs/players.md` — kona_player_info view, X-Fantasy-Filter header, projections and rankings
- Added `docs/matchups.md` — Scoring periods, matchup periods, boxscore, live scoring, playoffs
- Added `docs/draft.md` — Draft picks, snake vs. auction vs. offline, live draft, keeper leagues
- Added `docs/transactions.md` — Waiver claims, trades, free agent adds, FAAB behavior
- Added `docs/settings.md` — All settings objects: acquisition, draft, finance, roster, schedule, scoring, trade
- Added `docs/response_schemas.md` — Complete JSON response shapes for all major objects

#### Verification Summary
- **VERIFIED** via live browser JavaScript fetch: FLB League 101 (public, season 2025) across all view parameters
- **VERIFIED**: Auth error schema (401 `AUTH_LEAGUE_NOT_VISIBLE`) from private league 336358
- **VERIFIED**: Game metadata for all 4 sports (FFL, FBA, FLB, FHL) via `/apis/v3/games/{code}`
- **PARTIALLY VERIFIED**: FBA and FHL position IDs (pattern observed, not all confirmed via live responses)
- **Confirmed active** for season 2026: `currentSeasonId: 2026` across all four game codes

#### Sports Documented
- 🏈 Fantasy Football (`ffl`)
- 🏀 Fantasy Basketball (`fba`)
- ⚾ Fantasy Baseball (`flb`)
- 🏒 Fantasy Hockey (`fhl`)
