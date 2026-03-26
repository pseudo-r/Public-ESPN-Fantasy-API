"""Data ingestion services for ESPN Fantasy API.

Each service class fetches data from the ESPN Fantasy v3 API via the
FantasyClient and persists it to the database using idempotent upserts
(update_or_create). All services return an IngestionResult dataclass.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import structlog
from django.db import transaction

from apps.fantasy.models import (
    DraftPick,
    FantasyGame,
    FantasyLeague,
    FantasyMember,
    FantasyPlayer,
    FantasyTeam,
    FantasyTransaction,
    Matchup,
    RosterEntry,
)
from clients.fantasy_client import FantasyAPIError, FantasyClient, get_fantasy_client

logger = structlog.get_logger(__name__)

GAME_NAMES = {
    "ffl": "Fantasy Football",
    "fba": "Fantasy Basketball",
    "flb": "Fantasy Baseball",
    "fhl": "Fantasy Hockey",
}


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class IngestionResult:
    """Result of a single ingestion operation."""

    created: int = 0
    updated: int = 0
    errors: int = 0
    details: list[str] = field(default_factory=list)

    @property
    def total_processed(self) -> int:
        return self.created + self.updated

    def to_dict(self) -> dict[str, Any]:
        return {
            "created": self.created,
            "updated": self.updated,
            "errors": self.errors,
            "total_processed": self.total_processed,
            "details": self.details,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_or_create_game(game_code: str) -> FantasyGame:
    game, _ = FantasyGame.objects.get_or_create(
        game_code=game_code,
        defaults={"name": GAME_NAMES.get(game_code, game_code.upper())},
    )
    return game


def _ms_to_dt(ms: int | None) -> datetime | None:
    if not ms:
        return None
    try:
        return datetime.fromtimestamp(ms / 1000, tz=__import__("datetime").timezone.utc)
    except (OSError, OverflowError, ValueError):
        return None


# ---------------------------------------------------------------------------
# League + Team + Member ingestion
# ---------------------------------------------------------------------------

class LeagueIngestionService:
    """Ingests FantasyLeague, FantasyTeam, and FantasyMember from mSettings + mTeam + mStatus."""

    def __init__(self, client: FantasyClient | None = None) -> None:
        self.client = client or get_fantasy_client()

    def _parse_settings(self, settings: dict[str, Any]) -> dict[str, Any]:
        scoring = settings.get("scoringSettings", {})
        draft = settings.get("draftSettings", {})
        acq = settings.get("acquisitionSettings", {})
        schedule = settings.get("scheduleSettings", {})
        return {
            "name": settings.get("name", ""),
            "size": settings.get("size", 0),
            "is_public": settings.get("isPublic", True),
            "scoring_type": scoring.get("scoringType", ""),
            "acquisition_type": acq.get("acquisitionType", ""),
            "draft_type": draft.get("type", ""),
            "playoff_team_count": schedule.get("playoffTeamCount", 4),
            "matchup_period_count": schedule.get("matchupPeriodCount", 0),
            "raw_settings": settings,
        }

    def _parse_status(self, status: dict[str, Any]) -> dict[str, Any]:
        return {
            "current_scoring_period_id": status.get("latestScoringPeriod", 1),
            "current_matchup_period": status.get("currentMatchupPeriod", 1),
            "first_scoring_period": status.get("firstScoringPeriod", 1),
            "final_scoring_period": status.get("finalScoringPeriod", 1),
            "draft_completed": False,  # set separately from draftDetail
            "is_active": status.get("isActive", True),
            "is_expired": status.get("isExpired", False),
            "raw_status": status,
        }

    @transaction.atomic
    def ingest_league(self, game_code: str, season_id: int, league_id: int) -> IngestionResult:
        result = IngestionResult()
        try:
            response = self.client.get_league(
                game_code, season_id, league_id,
                views=["mSettings", "mTeam", "mStatus"],
            )
            data = response.league_data

            game = _get_or_create_game(game_code)
            settings = data.get("settings", {})
            status = data.get("status", {})
            draft_detail = data.get("draftDetail", {})

            parsed_settings = self._parse_settings(settings)
            parsed_status = self._parse_status(status)
            parsed_status["draft_completed"] = draft_detail.get("drafted", False)

            league, created = FantasyLeague.objects.update_or_create(
                game=game,
                espn_id=league_id,
                season_id=season_id,
                defaults={**parsed_settings, **parsed_status},
            )
            if created:
                result.created += 1
            else:
                result.updated += 1

            # Members
            for m in data.get("members", []):
                swid = m.get("id", "")
                if not swid:
                    continue
                FantasyMember.objects.update_or_create(
                    league=league,
                    swid=swid,
                    defaults={
                        "display_name": m.get("displayName", ""),
                        "first_name": m.get("firstName", ""),
                        "last_name": m.get("lastName", ""),
                    },
                )

            # Teams
            owner_map: dict[str, int] = {}
            for t in data.get("teams", []):
                espn_team_id = t.get("id")
                if not espn_team_id:
                    continue
                record = t.get("record", {}).get("overall", {})
                owners = t.get("owners", [])
                FantasyTeam.objects.update_or_create(
                    league=league,
                    espn_id=espn_team_id,
                    defaults={
                        "name": f"{t.get('location', '')} {t.get('nickname', '')}".strip()
                               or t.get("name", ""),
                        "abbrev": t.get("abbrev", ""),
                        "division_id": t.get("divisionId", 0),
                        "wins": record.get("wins", 0),
                        "losses": record.get("losses", 0),
                        "ties": record.get("ties", 0),
                        "points_for": record.get("pointsFor", 0.0),
                        "points_against": record.get("pointsAgainst", 0.0),
                        "standing": t.get("rankCalculatedFinal", 0),
                        "waiver_rank": t.get("waiverRank", 0),
                        "total_acquisitions": t.get("transactionCounter", {}).get("acquisitions", 0),
                        "total_trades": t.get("transactionCounter", {}).get("trades", 0),
                        "owner_swids": owners,
                        "raw_record": t.get("record", {}),
                    },
                )
                for swid in owners:
                    owner_map[swid] = espn_team_id

            logger.info("league_ingested", game_code=game_code, season=season_id, league_id=league_id)

        except FantasyAPIError as e:
            logger.error("league_ingestion_failed", error=str(e))
            result.errors += 1
            result.details.append(str(e))

        return result


# ---------------------------------------------------------------------------
# Roster ingestion
# ---------------------------------------------------------------------------

class RosterIngestionService:
    """Ingests RosterEntry records from mRoster."""

    def __init__(self, client: FantasyClient | None = None) -> None:
        self.client = client or get_fantasy_client()

    @transaction.atomic
    def ingest_roster(
        self,
        game_code: str,
        season_id: int,
        league_id: int,
        scoring_period_id: int,
    ) -> IngestionResult:
        result = IngestionResult()
        try:
            response = self.client.get_league(
                game_code, season_id, league_id,
                views=["mRoster"],
                scoring_period_id=scoring_period_id,
            )
            data = response.league_data

            try:
                league = FantasyLeague.objects.get(game__game_code=game_code, espn_id=league_id, season_id=season_id)
            except FantasyLeague.DoesNotExist:
                logger.warning("roster_ingest_no_league", game_code=game_code, league_id=league_id)
                result.errors += 1
                return result

            for team_data in data.get("teams", []):
                espn_team_id = team_data.get("id")
                try:
                    team = FantasyTeam.objects.get(league=league, espn_id=espn_team_id)
                except FantasyTeam.DoesNotExist:
                    continue

                for entry in team_data.get("roster", {}).get("entries", []):
                    player_id = entry.get("playerId")
                    if not player_id:
                        continue

                    ppe = entry.get("playerPoolEntry", {})
                    player_info = ppe.get("player", {})
                    player, _ = FantasyPlayer.objects.update_or_create(
                        espn_id=player_id,
                        defaults={
                            "full_name": player_info.get("fullName", ""),
                            "first_name": player_info.get("firstName", ""),
                            "last_name": player_info.get("lastName", ""),
                            "pro_team_id": player_info.get("proTeamId", 0),
                            "default_position_id": player_info.get("defaultPositionId", 0),
                            "eligible_slots": player_info.get("eligibleSlots", []),
                            "injury_status": ppe.get("injuryStatus", "ACTIVE"),
                            "percent_owned": ppe.get("percentOwned", 0.0),
                            "percent_started": ppe.get("percentStarted", 0.0),
                            "raw_data": ppe,
                        },
                    )

                    acq_date_ms = entry.get("acquisitionDate")
                    _, created = RosterEntry.objects.update_or_create(
                        team=team,
                        player=player,
                        scoring_period_id=scoring_period_id,
                        defaults={
                            "lineup_slot_id": entry.get("lineupSlotId", 0),
                            "acquisition_type": entry.get("acquisitionType", ""),
                            "acquisition_date": _ms_to_dt(acq_date_ms),
                            "applied_stat_total": ppe.get("appliedStatTotal", 0.0),
                            "injury_status": ppe.get("injuryStatus", ""),
                        },
                    )
                    if created:
                        result.created += 1
                    else:
                        result.updated += 1

        except FantasyAPIError as e:
            logger.error("roster_ingestion_failed", error=str(e))
            result.errors += 1

        return result


# ---------------------------------------------------------------------------
# Matchup ingestion
# ---------------------------------------------------------------------------

class MatchupIngestionService:
    """Ingests Matchup records from mMatchupScore."""

    def __init__(self, client: FantasyClient | None = None) -> None:
        self.client = client or get_fantasy_client()

    @transaction.atomic
    def ingest_matchups(
        self,
        game_code: str,
        season_id: int,
        league_id: int,
        matchup_period_id: int | None = None,
    ) -> IngestionResult:
        result = IngestionResult()
        try:
            response = self.client.get_league(
                game_code, season_id, league_id,
                views=["mMatchupScore"],
                matchup_period_id=matchup_period_id,
            )
            data = response.league_data

            try:
                league = FantasyLeague.objects.get(game__game_code=game_code, espn_id=league_id, season_id=season_id)
            except FantasyLeague.DoesNotExist:
                result.errors += 1
                return result

            for sched in data.get("schedule", []):
                espn_matchup_id = sched.get("id")
                if not espn_matchup_id:
                    continue

                home = sched.get("home", {})
                away = sched.get("away", {})
                playoff_tier = sched.get("playoffTierType", "NONE")

                def _get_team(team_data: dict[str, Any]) -> FantasyTeam | None:
                    tid = team_data.get("teamId")
                    if not tid:
                        return None
                    return FantasyTeam.objects.filter(league=league, espn_id=tid).first()

                home_team = _get_team(home)
                away_team = _get_team(away)

                _, created = Matchup.objects.update_or_create(
                    league=league,
                    espn_id=espn_matchup_id,
                    defaults={
                        "matchup_period_id": sched.get("matchupPeriodId", 0),
                        "home_team": home_team,
                        "away_team": away_team,
                        "home_points": home.get("totalPoints", 0.0),
                        "away_points": away.get("totalPoints", 0.0),
                        "home_projected_points": home.get("totalProjectedPointsLive", 0.0),
                        "away_projected_points": away.get("totalProjectedPointsLive", 0.0),
                        "winner": sched.get("winner", "UNDECIDED"),
                        "playoff_tier_type": playoff_tier,
                        "is_playoff": playoff_tier not in ("NONE", ""),
                    },
                )
                if created:
                    result.created += 1
                else:
                    result.updated += 1

        except FantasyAPIError as e:
            logger.error("matchup_ingestion_failed", error=str(e))
            result.errors += 1

        return result


# ---------------------------------------------------------------------------
# Draft ingestion
# ---------------------------------------------------------------------------

class DraftIngestionService:
    """Ingests DraftPick records from mDraftDetail."""

    def __init__(self, client: FantasyClient | None = None) -> None:
        self.client = client or get_fantasy_client()

    @transaction.atomic
    def ingest_draft(self, game_code: str, season_id: int, league_id: int) -> IngestionResult:
        result = IngestionResult()
        try:
            response = self.client.get_league(
                game_code, season_id, league_id, views=["mDraftDetail"]
            )
            data = response.league_data

            try:
                league = FantasyLeague.objects.get(game__game_code=game_code, espn_id=league_id, season_id=season_id)
            except FantasyLeague.DoesNotExist:
                result.errors += 1
                return result

            draft_detail = data.get("draftDetail", {})
            picks = draft_detail.get("picks", [])

            # Mark league as drafted
            if draft_detail.get("drafted"):
                FantasyLeague.objects.filter(pk=league.pk).update(draft_completed=True)

            for pick in picks:
                overall = pick.get("overallPickNumber") or pick.get("id")
                player_id = pick.get("playerId")
                if not overall or not player_id:
                    continue

                team = FantasyTeam.objects.filter(league=league, espn_id=pick.get("teamId")).first()
                nom_team = FantasyTeam.objects.filter(
                    league=league, espn_id=pick.get("nominatingTeamId")
                ).first() if pick.get("nominatingTeamId") else None

                _, created = DraftPick.objects.update_or_create(
                    league=league,
                    overall_pick=overall,
                    defaults={
                        "team": team,
                        "nominating_team": nom_team,
                        "player_espn_id": player_id,
                        "round_id": pick.get("roundId", 0),
                        "round_pick": pick.get("roundPickNumber", 0),
                        "bid_amount": pick.get("bidAmount", 0),
                        "auto_drafted": pick.get("autoDraftTypeId", 0) == 1,
                        "keeper": pick.get("keeper", False),
                    },
                )
                if created:
                    result.created += 1
                else:
                    result.updated += 1

        except FantasyAPIError as e:
            logger.error("draft_ingestion_failed", error=str(e))
            result.errors += 1

        return result


# ---------------------------------------------------------------------------
# Transaction ingestion
# ---------------------------------------------------------------------------

class TransactionIngestionService:
    """Ingests FantasyTransaction records from mTransactions2."""

    def __init__(self, client: FantasyClient | None = None) -> None:
        self.client = client or get_fantasy_client()

    @transaction.atomic
    def ingest_transactions(
        self,
        game_code: str,
        season_id: int,
        league_id: int,
        scoring_period_id: int,
    ) -> IngestionResult:
        result = IngestionResult()
        try:
            response = self.client.get_league(
                game_code, season_id, league_id,
                views=["mTransactions2"],
                scoring_period_id=scoring_period_id,
            )
            data = response.league_data

            try:
                league = FantasyLeague.objects.get(game__game_code=game_code, espn_id=league_id, season_id=season_id)
            except FantasyLeague.DoesNotExist:
                result.errors += 1
                return result

            for txn in data.get("transactions", []):
                uuid = txn.get("id", "")
                if not uuid:
                    continue

                _, created = FantasyTransaction.objects.update_or_create(
                    league=league,
                    uuid=uuid,
                    defaults={
                        "scoring_period_id": txn.get("scoringPeriodId", scoring_period_id),
                        "type": txn.get("type", ""),
                        "status": txn.get("status", ""),
                        "team_espn_id": txn.get("teamId", 0),
                        "bid_amount": txn.get("bidAmount", 0),
                        "waiver_priority": txn.get("proposedDate", 0),
                        "process_date": _ms_to_dt(txn.get("processDate")),
                        "proposed_date": _ms_to_dt(txn.get("proposedDate")),
                        "items": txn.get("items", []),
                        "raw_data": txn,
                    },
                )
                if created:
                    result.created += 1
                else:
                    result.updated += 1

        except FantasyAPIError as e:
            logger.error("transaction_ingestion_failed", error=str(e))
            result.errors += 1

        return result


# ---------------------------------------------------------------------------
# Player pool ingestion
# ---------------------------------------------------------------------------

class PlayerPoolIngestionService:
    """Ingests FantasyPlayer records from kona_player_info."""

    def __init__(self, client: FantasyClient | None = None) -> None:
        self.client = client or get_fantasy_client()

    @transaction.atomic
    def ingest_players(
        self,
        game_code: str,
        season_id: int,
        league_id: int,
        limit: int = 300,
        offset: int = 0,
    ) -> IngestionResult:
        result = IngestionResult()
        try:
            response = self.client.get_player_pool(
                game_code, season_id, league_id, limit=limit, offset=offset
            )
            data = response.league_data

            for ppe in data.get("players", []):
                player_info = ppe.get("player", {})
                player_id = ppe.get("id") or player_info.get("id")
                if not player_id:
                    continue

                _, created = FantasyPlayer.objects.update_or_create(
                    espn_id=player_id,
                    defaults={
                        "full_name": player_info.get("fullName", ""),
                        "first_name": player_info.get("firstName", ""),
                        "last_name": player_info.get("lastName", ""),
                        "pro_team_id": player_info.get("proTeamId", 0),
                        "default_position_id": player_info.get("defaultPositionId", 0),
                        "is_active": player_info.get("active", True),
                        "is_droppable": ppe.get("keeperValue", 0) == 0,
                        "injury_status": ppe.get("injuryStatus", "ACTIVE"),
                        "percent_owned": ppe.get("percentOwned", 0.0),
                        "percent_started": ppe.get("percentStarted", 0.0),
                        "avg_draft_position": ppe.get("averageDraftPosition", 0.0),
                        "eligible_slots": player_info.get("eligibleSlots", []),
                        "raw_data": ppe,
                    },
                )
                if created:
                    result.created += 1
                else:
                    result.updated += 1

        except FantasyAPIError as e:
            logger.error("player_pool_ingestion_failed", error=str(e))
            result.errors += 1

        return result
