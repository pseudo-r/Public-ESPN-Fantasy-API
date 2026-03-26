# CHANGELOG

All notable documentation changes to this project are recorded here.

## [1.2.0] — 2026-03-26

### Documentation — Internet-wide verification pass

#### Cross-verified against
- `cwendt94/espn-api` library source code (espn_requests.py, base_league.py, league.py)
- Community sources (ffverse, thomaswildetech.com, onyxmueller.net, Reddit r/fantasyfootball)

#### New views added to `docs/leagues.md`
- `mLiveScoring` — real-time live scoring during active scoring periods; use with `mBoxscore` + `mScoreboard`
- `mSchedule` — full season schedule for all teams (no `matchupPeriodId` required)
- `mStandings` — season standings, records, and point totals (lighter alternative to `mTeam`)
- `modular` + `mNav` — ESPN website meta-views; documented with practical caveat for programmatic use

#### Complete View Reference table added
- Added a 21-row reference table at the bottom of `docs/leagues.md` mapping every known view to its primary response key, auth requirement, and description

#### Verification corrections
- Confirmed `players_wl` spelling (not `player_wl`) via source code
- Confirmed `mStandings` is used alongside `mTeam`, `mRoster`, `mMatchup`, `mSettings` in the espn-api initial league fetch
- Confirmed `proTeamSchedules_wl` view is used for pro team bye-week calculation

---

## [1.1.0] — 2026-03-26


### Documentation Expansion

#### New Documents
- Added `docs/historical_seasons.md` — `leagueHistory` endpoint for pre-2018 seasons, hybrid fetch strategy, auth restriction as of August 2025
- Added `docs/known_issues.md` — breaking change history (v2→v3, April 2024 domain switch, Aug 2025 auth restriction), instabilities, sport-specific gaps, undocumented behaviors
- Added `docs/stat_ids.md` — numeric stat category ID reference for FFL, FLB, FBA, FHL

#### Updated Documents
- `docs/leagues.md` — Added 5 new views: `mMatchup`, `mPositionalRatings`, `kona_playercard`, `kona_league_messageboard`; added sub-path endpoints: `players_wl`, player news, message board
- `docs/draft.md` — Added `nominatingTeamId` field (auction leagues only; discovered via source code)
- `README.md` — Added `lm-api-reads` domain note, historical endpoint pattern, sub-path endpoints table, all new views with VERIFIED status labels

#### New Endpoints Discovered (via web research + source code analysis)
- `leagueHistory/{leagueId}?seasonId=` — pre-2018 historical data
- `/seasons/{year}/players?view=players_wl` — all active pro players roster
- `/news/players?playerId=` — player news
- `/communication?view=kona_league_messageboard` — league message board
- `kona_playercard` view — per-player deep stat cards
- `mPositionalRatings` view — defensive positional ratings
- `mMatchup` — confirmed as working alias for `mMatchupScore`

---

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
