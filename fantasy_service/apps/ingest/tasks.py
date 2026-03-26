"""Celery tasks for ESPN Fantasy data ingestion."""

from __future__ import annotations

import structlog
from celery import shared_task, chord, group

from apps.ingest.services import (
    DraftIngestionService,
    LeagueIngestionService,
    MatchupIngestionService,
    PlayerPoolIngestionService,
    RosterIngestionService,
    TransactionIngestionService,
)

logger = structlog.get_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def sync_league(self, game_code: str, season_id: int, league_id: int) -> dict:  # type: ignore[override]
    """Ingest league settings, teams, and members."""
    try:
        result = LeagueIngestionService().ingest_league(game_code, season_id, league_id)
        logger.info("sync_league_done", game_code=game_code, season=season_id, league=league_id, **result.to_dict())
        return result.to_dict()
    except Exception as exc:
        logger.warning("sync_league_retry", exc=str(exc), attempt=self.request.retries)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def sync_roster(
    self,
    game_code: str,
    season_id: int,
    league_id: int,
    scoring_period_id: int,
) -> dict:  # type: ignore[override]
    """Ingest roster entries for a scoring period."""
    try:
        result = RosterIngestionService().ingest_roster(game_code, season_id, league_id, scoring_period_id)
        logger.info("sync_roster_done", **result.to_dict())
        return result.to_dict()
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def sync_matchups(
    self,
    game_code: str,
    season_id: int,
    league_id: int,
    matchup_period_id: int | None = None,
) -> dict:  # type: ignore[override]
    """Ingest all matchups (or a specific matchup period)."""
    try:
        result = MatchupIngestionService().ingest_matchups(
            game_code, season_id, league_id, matchup_period_id=matchup_period_id
        )
        logger.info("sync_matchups_done", **result.to_dict())
        return result.to_dict()
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def sync_draft(self, game_code: str, season_id: int, league_id: int) -> dict:  # type: ignore[override]
    """Ingest the full draft history."""
    try:
        result = DraftIngestionService().ingest_draft(game_code, season_id, league_id)
        logger.info("sync_draft_done", **result.to_dict())
        return result.to_dict()
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def sync_transactions(
    self,
    game_code: str,
    season_id: int,
    league_id: int,
    scoring_period_id: int,
) -> dict:  # type: ignore[override]
    """Ingest transactions for a scoring period."""
    try:
        result = TransactionIngestionService().ingest_transactions(
            game_code, season_id, league_id, scoring_period_id
        )
        logger.info("sync_transactions_done", **result.to_dict())
        return result.to_dict()
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def sync_players(
    self,
    game_code: str,
    season_id: int,
    league_id: int,
    limit: int = 300,
) -> dict:  # type: ignore[override]
    """Ingest the player pool."""
    try:
        result = PlayerPoolIngestionService().ingest_players(game_code, season_id, league_id, limit=limit)
        logger.info("sync_players_done", **result.to_dict())
        return result.to_dict()
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task
def sync_league_full(
    game_code: str,
    season_id: int,
    league_id: int,
    scoring_period_id: int = 1,
) -> str:
    """Run a full league sync: settings → draft → matchups → roster → players → transactions.

    Runs league first (dependency), then fires remaining tasks in parallel.
    """
    # Step 1: League (teams + settings must exist before roster/matchups)
    sync_league.apply(args=[game_code, season_id, league_id])

    # Step 2: Fire remaining tasks in parallel
    parallel_tasks = group(
        sync_draft.s(game_code, season_id, league_id),
        sync_matchups.s(game_code, season_id, league_id),
        sync_roster.s(game_code, season_id, league_id, scoring_period_id),
        sync_players.s(game_code, season_id, league_id),
        sync_transactions.s(game_code, season_id, league_id, scoring_period_id),
    )
    parallel_tasks.apply_async()

    return f"Full sync dispatched for {game_code} league {league_id} season {season_id}"
