"""Ingest trigger API views."""

from __future__ import annotations

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ingest.tasks import sync_league_full, sync_players, sync_roster, sync_transactions


class IngestLeagueView(APIView):
    """Trigger a full league sync (settings, teams, draft, matchups, roster, players, transactions)."""

    @extend_schema(
        tags=["Ingest"],
        summary="Trigger full league sync",
        parameters=[
            OpenApiParameter("game_code", required=True, description="ffl, fba, flb, or fhl", type=str),
            OpenApiParameter("season_id", required=True, description="Season year (e.g., 2025)", type=int),
            OpenApiParameter("league_id", required=True, description="ESPN league ID", type=int),
            OpenApiParameter("scoring_period_id", description="Scoring period to sync (default: 1)", type=int),
        ],
        responses={202: {"description": "Sync dispatched"}},
    )
    def post(self, request: Request) -> Response:
        game_code = request.data.get("game_code") or request.query_params.get("game_code")
        season_id = request.data.get("season_id") or request.query_params.get("season_id")
        league_id = request.data.get("league_id") or request.query_params.get("league_id")
        scoring_period_id = int(request.data.get("scoring_period_id", 1))

        if not all([game_code, season_id, league_id]):
            return Response(
                {"error": "game_code, season_id, and league_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = sync_league_full.delay(
            str(game_code), int(season_id), int(league_id), scoring_period_id
        )
        return Response(
            {"task_id": task.id, "status": "dispatched"},
            status=status.HTTP_202_ACCEPTED,
        )


class IngestRosterView(APIView):
    """Trigger roster ingestion for a specific scoring period."""

    @extend_schema(
        tags=["Ingest"],
        summary="Trigger roster sync for a scoring period",
        responses={202: {"description": "Sync dispatched"}},
    )
    def post(self, request: Request) -> Response:
        game_code = request.data.get("game_code")
        season_id = request.data.get("season_id")
        league_id = request.data.get("league_id")
        scoring_period_id = request.data.get("scoring_period_id")

        if not all([game_code, season_id, league_id, scoring_period_id]):
            return Response(
                {"error": "game_code, season_id, league_id, scoring_period_id required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = sync_roster.delay(str(game_code), int(season_id), int(league_id), int(scoring_period_id))
        return Response({"task_id": task.id, "status": "dispatched"}, status=status.HTTP_202_ACCEPTED)


class IngestPlayersView(APIView):
    """Trigger player pool ingestion."""

    @extend_schema(
        tags=["Ingest"],
        summary="Trigger player pool sync",
        responses={202: {"description": "Sync dispatched"}},
    )
    def post(self, request: Request) -> Response:
        game_code = request.data.get("game_code")
        season_id = request.data.get("season_id")
        league_id = request.data.get("league_id")
        limit = int(request.data.get("limit", 300))

        if not all([game_code, season_id, league_id]):
            return Response(
                {"error": "game_code, season_id, league_id required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = sync_players.delay(str(game_code), int(season_id), int(league_id), limit)
        return Response({"task_id": task.id, "status": "dispatched"}, status=status.HTTP_202_ACCEPTED)


class IngestTransactionsView(APIView):
    """Trigger transaction ingestion for a scoring period."""

    @extend_schema(
        tags=["Ingest"],
        summary="Trigger transaction sync for a scoring period",
        responses={202: {"description": "Sync dispatched"}},
    )
    def post(self, request: Request) -> Response:
        game_code = request.data.get("game_code")
        season_id = request.data.get("season_id")
        league_id = request.data.get("league_id")
        scoring_period_id = request.data.get("scoring_period_id")

        if not all([game_code, season_id, league_id, scoring_period_id]):
            return Response(
                {"error": "game_code, season_id, league_id, scoring_period_id required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = sync_transactions.delay(
            str(game_code), int(season_id), int(league_id), int(scoring_period_id)
        )
        return Response({"task_id": task.id, "status": "dispatched"}, status=status.HTTP_202_ACCEPTED)
