"""DRF ViewSets for ESPN Fantasy data."""

from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from apps.fantasy.models import (
    DraftPick,
    FantasyGame,
    FantasyLeague,
    FantasyPlayer,
    FantasyTeam,
    FantasyTransaction,
    Matchup,
    RosterEntry,
)
from apps.fantasy.serializers import (
    DraftPickSerializer,
    FantasyGameSerializer,
    FantasyLeagueListSerializer,
    FantasyLeagueSerializer,
    FantasyPlayerListSerializer,
    FantasyPlayerSerializer,
    FantasyTeamListSerializer,
    FantasyTeamSerializer,
    FantasyTransactionSerializer,
    MatchupListSerializer,
    MatchupSerializer,
    RosterEntrySerializer,
)


class FantasyGameViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve ESPN Fantasy game types (ffl, fba, flb, fhl)."""

    serializer_class = FantasyGameSerializer
    queryset = FantasyGame.objects.all().order_by("game_code")
    lookup_field = "game_code"

    @extend_schema(tags=["Fantasy"], summary="List fantasy game types")
    def list(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=["Fantasy"], summary="Get fantasy game type by game_code")
    def retrieve(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().retrieve(request, *args, **kwargs)


class FantasyLeagueViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve ingested fantasy leagues."""

    search_fields = ["name"]
    ordering_fields = ["season_id", "name", "created_at"]
    ordering = ["-season_id", "name"]

    def get_queryset(self) -> QuerySet[FantasyLeague]:
        qs = FantasyLeague.objects.select_related("game").prefetch_related("members")

        game_code = self.request.query_params.get("game_code")
        if game_code:
            qs = qs.filter(game__game_code__iexact=game_code)

        season = self.request.query_params.get("season")
        if season and season.isdigit():
            qs = qs.filter(season_id=int(season))

        is_public = self.request.query_params.get("is_public")
        if is_public is not None:
            qs = qs.filter(is_public=is_public.lower() == "true")

        return qs

    def get_serializer_class(self) -> type:
        if self.action == "list":
            return FantasyLeagueListSerializer
        return FantasyLeagueSerializer

    @extend_schema(
        tags=["Fantasy"],
        summary="List fantasy leagues",
        parameters=[
            OpenApiParameter("game_code", description="Filter by game code (ffl, fba, flb, fhl)", type=str),
            OpenApiParameter("season", description="Filter by season year (e.g., 2025)", type=int),
            OpenApiParameter("is_public", description="Filter by public/private status", type=bool),
            OpenApiParameter("search", description="Search league name", type=str),
        ],
    )
    def list(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=["Fantasy"], summary="Get fantasy league detail")
    def retrieve(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().retrieve(request, *args, **kwargs)


class FantasyTeamViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve fantasy teams."""

    search_fields = ["name", "abbrev"]
    ordering_fields = ["standing", "points_for", "wins", "name"]
    ordering = ["standing", "name"]

    def get_queryset(self) -> QuerySet[FantasyTeam]:
        qs = FantasyTeam.objects.select_related("league", "league__game")

        league_id = self.request.query_params.get("league")
        if league_id and league_id.isdigit():
            qs = qs.filter(league__id=int(league_id))

        game_code = self.request.query_params.get("game_code")
        if game_code:
            qs = qs.filter(league__game__game_code__iexact=game_code)

        season = self.request.query_params.get("season")
        if season and season.isdigit():
            qs = qs.filter(league__season_id=int(season))

        return qs

    def get_serializer_class(self) -> type:
        if self.action == "list":
            return FantasyTeamListSerializer
        return FantasyTeamSerializer

    @extend_schema(
        tags=["Fantasy"],
        summary="List fantasy teams",
        parameters=[
            OpenApiParameter("league", description="Filter by league DB ID", type=int),
            OpenApiParameter("game_code", description="Filter by game code", type=str),
            OpenApiParameter("season", description="Filter by season year", type=int),
            OpenApiParameter("search", description="Search team name/abbreviation", type=str),
        ],
    )
    def list(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=["Fantasy"], summary="Get fantasy team detail")
    def retrieve(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().retrieve(request, *args, **kwargs)


class FantasyPlayerViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve players in the ESPN player pool."""

    search_fields = ["full_name", "first_name", "last_name"]
    ordering_fields = ["percent_owned", "avg_draft_position", "full_name"]
    ordering = ["-percent_owned"]

    def get_queryset(self) -> QuerySet[FantasyPlayer]:
        qs = FantasyPlayer.objects.all()

        injury_status = self.request.query_params.get("injury_status")
        if injury_status:
            qs = qs.filter(injury_status__iexact=injury_status)

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")

        position_id = self.request.query_params.get("position_id")
        if position_id and position_id.isdigit():
            qs = qs.filter(default_position_id=int(position_id))

        return qs

    def get_serializer_class(self) -> type:
        if self.action == "list":
            return FantasyPlayerListSerializer
        return FantasyPlayerSerializer

    @extend_schema(
        tags=["Fantasy"],
        summary="List players in the ESPN player pool",
        parameters=[
            OpenApiParameter("injury_status", description="Filter: ACTIVE, OUT, QUESTIONABLE, IR, etc.", type=str),
            OpenApiParameter("is_active", description="Filter active/inactive players", type=bool),
            OpenApiParameter("position_id", description="Filter by defaultPositionId", type=int),
            OpenApiParameter("search", description="Search by name", type=str),
        ],
    )
    def list(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=["Fantasy"], summary="Get player detail")
    def retrieve(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().retrieve(request, *args, **kwargs)


class RosterEntryViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve roster entries (player → team for a scoring period)."""

    serializer_class = RosterEntrySerializer
    ordering_fields = ["lineup_slot_id", "applied_stat_total"]
    ordering = ["lineup_slot_id"]

    def get_queryset(self) -> QuerySet[RosterEntry]:
        qs = RosterEntry.objects.select_related("team", "player", "team__league")

        team_id = self.request.query_params.get("team")
        if team_id and team_id.isdigit():
            qs = qs.filter(team__id=int(team_id))

        league_id = self.request.query_params.get("league")
        if league_id and league_id.isdigit():
            qs = qs.filter(team__league__id=int(league_id))

        period = self.request.query_params.get("scoring_period_id")
        if period and period.isdigit():
            qs = qs.filter(scoring_period_id=int(period))

        return qs

    @extend_schema(
        tags=["Fantasy"],
        summary="List roster entries",
        parameters=[
            OpenApiParameter("team", description="Filter by team DB ID", type=int),
            OpenApiParameter("league", description="Filter by league DB ID", type=int),
            OpenApiParameter("scoring_period_id", description="Filter by scoring period", type=int),
        ],
    )
    def list(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=["Fantasy"], summary="Get roster entry detail")
    def retrieve(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().retrieve(request, *args, **kwargs)


class MatchupViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve matchups (schedule entries)."""

    ordering_fields = ["matchup_period_id", "home_points", "away_points"]
    ordering = ["matchup_period_id", "espn_id"]

    def get_queryset(self) -> QuerySet[Matchup]:
        qs = Matchup.objects.select_related("league", "home_team", "away_team")

        league_id = self.request.query_params.get("league")
        if league_id and league_id.isdigit():
            qs = qs.filter(league__id=int(league_id))

        period = self.request.query_params.get("matchup_period_id")
        if period and period.isdigit():
            qs = qs.filter(matchup_period_id=int(period))

        is_playoff = self.request.query_params.get("is_playoff")
        if is_playoff is not None:
            qs = qs.filter(is_playoff=is_playoff.lower() == "true")

        return qs

    def get_serializer_class(self) -> type:
        if self.action == "list":
            return MatchupListSerializer
        return MatchupSerializer

    @extend_schema(
        tags=["Fantasy"],
        summary="List matchups",
        parameters=[
            OpenApiParameter("league", description="Filter by league DB ID", type=int),
            OpenApiParameter("matchup_period_id", description="Filter by matchup period", type=int),
            OpenApiParameter("is_playoff", description="Filter playoff matchups", type=bool),
        ],
    )
    def list(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=["Fantasy"], summary="Get matchup detail")
    def retrieve(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().retrieve(request, *args, **kwargs)


class DraftPickViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve draft picks."""

    serializer_class = DraftPickSerializer
    ordering_fields = ["overall_pick", "round_id", "bid_amount"]
    ordering = ["overall_pick"]

    def get_queryset(self) -> QuerySet[DraftPick]:
        qs = DraftPick.objects.select_related("league", "team", "nominating_team")

        league_id = self.request.query_params.get("league")
        if league_id and league_id.isdigit():
            qs = qs.filter(league__id=int(league_id))

        round_id = self.request.query_params.get("round")
        if round_id and round_id.isdigit():
            qs = qs.filter(round_id=int(round_id))

        team_id = self.request.query_params.get("team")
        if team_id and team_id.isdigit():
            qs = qs.filter(team__id=int(team_id))

        return qs

    @extend_schema(
        tags=["Fantasy"],
        summary="List draft picks",
        parameters=[
            OpenApiParameter("league", description="Filter by league DB ID", type=int),
            OpenApiParameter("round", description="Filter by round number", type=int),
            OpenApiParameter("team", description="Filter by team DB ID", type=int),
        ],
    )
    def list(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=["Fantasy"], summary="Get draft pick detail")
    def retrieve(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().retrieve(request, *args, **kwargs)


class FantasyTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve fantasy transactions (waivers, trades, free agent adds)."""

    serializer_class = FantasyTransactionSerializer
    search_fields = ["uuid"]
    ordering_fields = ["process_date", "scoring_period_id"]
    ordering = ["-process_date"]

    def get_queryset(self) -> QuerySet[FantasyTransaction]:
        qs = FantasyTransaction.objects.select_related("league")

        league_id = self.request.query_params.get("league")
        if league_id and league_id.isdigit():
            qs = qs.filter(league__id=int(league_id))

        txn_type = self.request.query_params.get("type")
        if txn_type:
            qs = qs.filter(type__iexact=txn_type)

        txn_status = self.request.query_params.get("status")
        if txn_status:
            qs = qs.filter(status__iexact=txn_status)

        period = self.request.query_params.get("scoring_period_id")
        if period and period.isdigit():
            qs = qs.filter(scoring_period_id=int(period))

        return qs

    @extend_schema(
        tags=["Fantasy"],
        summary="List transactions",
        parameters=[
            OpenApiParameter("league", description="Filter by league DB ID", type=int),
            OpenApiParameter("type", description="Filter by type: WAIVER, FREE_AGENT, TRADE, DRAFT", type=str),
            OpenApiParameter("status", description="Filter by status: EXECUTED, CANCELED, PENDING, VETOED", type=str),
            OpenApiParameter("scoring_period_id", description="Filter by scoring period", type=int),
        ],
    )
    def list(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=["Fantasy"], summary="Get transaction detail")
    def retrieve(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().retrieve(request, *args, **kwargs)
