"""Django management command: sync_fantasy.

Usage:
    python manage.py sync_fantasy --game ffl --season 2025 --league 336358
    python manage.py sync_fantasy --game flb --season 2025 --league 101 --period 50
    python manage.py sync_fantasy --game ffl --season 2025 --league 336358 --only league
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from apps.ingest.services import (
    DraftIngestionService,
    LeagueIngestionService,
    MatchupIngestionService,
    PlayerPoolIngestionService,
    RosterIngestionService,
    TransactionIngestionService,
)


class Command(BaseCommand):
    help = "Sync ESPN Fantasy league data (settings, teams, draft, matchups, roster, transactions, players)"

    def add_arguments(self, parser):  # type: ignore[override]
        parser.add_argument("--game", required=True, choices=["ffl", "fba", "flb", "fhl"], help="Game code")
        parser.add_argument("--season", required=True, type=int, help="Season year (e.g., 2025)")
        parser.add_argument("--league", required=True, type=int, help="ESPN league ID")
        parser.add_argument("--period", type=int, default=1, help="Scoring period ID (default: 1)")
        parser.add_argument(
            "--only",
            choices=["league", "roster", "matchups", "draft", "transactions", "players", "all"],
            default="all",
            help="Which data to sync (default: all)",
        )

    def handle(self, *args, **kwargs):  # type: ignore[override]
        game_code: str = kwargs["game"]
        season_id: int = kwargs["season"]
        league_id: int = kwargs["league"]
        period: int = kwargs["period"]
        only: str = kwargs["only"]

        self.stdout.write(
            self.style.HTTP_INFO(
                f"\nStarting ESPN Fantasy sync: {game_code.upper()} | Season {season_id} | League {league_id}"
            )
        )

        def _run(label: str, svc, *svc_args):  # type: ignore[no-untyped-def]
            self.stdout.write(f"  → {label}... ", ending="")
            result = svc(*svc_args)
            self.stdout.write(
                self.style.SUCCESS(
                    f"created={result.created} updated={result.updated} errors={result.errors}"
                )
            )
            if result.details:
                for d in result.details:
                    self.stdout.write(f"     {d}")
            return result

        run_all = only == "all"

        try:
            if run_all or only == "league":
                _run("League/Teams/Members", LeagueIngestionService().ingest_league, game_code, season_id, league_id)

            if run_all or only == "draft":
                _run("Draft picks", DraftIngestionService().ingest_draft, game_code, season_id, league_id)

            if run_all or only == "matchups":
                _run("Matchups", MatchupIngestionService().ingest_matchups, game_code, season_id, league_id)

            if run_all or only == "roster":
                _run(f"Roster (period {period})", RosterIngestionService().ingest_roster, game_code, season_id, league_id, period)

            if run_all or only == "players":
                _run("Player pool", PlayerPoolIngestionService().ingest_players, game_code, season_id, league_id)

            if run_all or only == "transactions":
                _run(f"Transactions (period {period})", TransactionIngestionService().ingest_transactions, game_code, season_id, league_id, period)

        except Exception as exc:
            raise CommandError(f"Sync failed: {exc}") from exc

        self.stdout.write(self.style.SUCCESS("\nSync complete."))
