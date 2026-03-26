"""DRF serializers for ESPN Fantasy models."""

from rest_framework import serializers

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


class FantasyGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = FantasyGame
        fields = ["id", "game_code", "name", "pro_sport_name", "current_season_id", "is_active"]


class FantasyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = FantasyMember
        fields = ["id", "swid", "display_name", "first_name", "last_name", "is_league_manager"]


class FantasyLeagueListSerializer(serializers.ModelSerializer):
    game_code = serializers.CharField(source="game.game_code", read_only=True)

    class Meta:
        model = FantasyLeague
        fields = [
            "id", "espn_id", "season_id", "game_code", "name", "size",
            "is_public", "scoring_type", "draft_type", "draft_completed",
            "current_scoring_period_id", "is_active",
        ]


class FantasyLeagueSerializer(serializers.ModelSerializer):
    game = FantasyGameSerializer(read_only=True)
    members = FantasyMemberSerializer(many=True, read_only=True)

    class Meta:
        model = FantasyLeague
        fields = [
            "id", "espn_id", "season_id", "game", "name", "size",
            "is_public", "scoring_type", "acquisition_type",
            "draft_type", "draft_completed", "playoff_team_count",
            "matchup_period_count", "current_scoring_period_id",
            "current_matchup_period", "first_scoring_period",
            "final_scoring_period", "is_active", "is_expired",
            "members", "raw_settings", "raw_status",
            "created_at", "updated_at",
        ]


class FantasyTeamListSerializer(serializers.ModelSerializer):
    record = serializers.CharField(read_only=True)

    class Meta:
        model = FantasyTeam
        fields = [
            "id", "espn_id", "name", "abbrev", "division_id",
            "wins", "losses", "ties", "record", "points_for",
            "points_against", "standing", "waiver_rank",
        ]


class FantasyTeamSerializer(serializers.ModelSerializer):
    record = serializers.CharField(read_only=True)
    league = FantasyLeagueListSerializer(read_only=True)

    class Meta:
        model = FantasyTeam
        fields = [
            "id", "espn_id", "league", "name", "abbrev", "division_id",
            "wins", "losses", "ties", "record", "points_for",
            "points_against", "standing", "waiver_rank",
            "total_acquisitions", "total_trades", "owner_swids",
            "raw_record", "created_at", "updated_at",
        ]


class FantasyPlayerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FantasyPlayer
        fields = [
            "id", "espn_id", "full_name", "default_position_id",
            "pro_team_id", "injury_status", "percent_owned",
            "avg_draft_position", "is_active", "is_droppable",
        ]


class FantasyPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FantasyPlayer
        fields = [
            "id", "espn_id", "full_name", "first_name", "last_name",
            "default_position_id", "pro_team_id", "is_active",
            "is_droppable", "injury_status", "percent_owned",
            "percent_started", "avg_draft_position", "eligible_slots",
            "raw_data", "created_at", "updated_at",
        ]


class RosterEntrySerializer(serializers.ModelSerializer):
    player = FantasyPlayerListSerializer(read_only=True)

    class Meta:
        model = RosterEntry
        fields = [
            "id", "team_id", "player", "scoring_period_id",
            "lineup_slot_id", "acquisition_type", "acquisition_date",
            "applied_stat_total", "injury_status",
        ]


class MatchupListSerializer(serializers.ModelSerializer):
    home_team_name = serializers.CharField(source="home_team.name", read_only=True, default="")
    away_team_name = serializers.CharField(source="away_team.name", read_only=True, default="")

    class Meta:
        model = Matchup
        fields = [
            "id", "espn_id", "matchup_period_id",
            "home_team_id", "home_team_name", "home_points",
            "away_team_id", "away_team_name", "away_points",
            "winner", "playoff_tier_type", "is_playoff",
        ]


class MatchupSerializer(serializers.ModelSerializer):
    home_team = FantasyTeamListSerializer(read_only=True)
    away_team = FantasyTeamListSerializer(read_only=True)

    class Meta:
        model = Matchup
        fields = [
            "id", "espn_id", "league_id", "matchup_period_id",
            "home_team", "home_points", "home_projected_points",
            "away_team", "away_points", "away_projected_points",
            "winner", "playoff_tier_type", "is_playoff",
            "created_at", "updated_at",
        ]


class DraftPickSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True, default="")
    nominating_team_name = serializers.CharField(source="nominating_team.name", read_only=True, default="")

    class Meta:
        model = DraftPick
        fields = [
            "id", "league_id", "overall_pick", "round_id", "round_pick",
            "team_id", "team_name", "nominating_team_id", "nominating_team_name",
            "player_espn_id", "player_name", "bid_amount",
            "auto_drafted", "keeper",
        ]


class FantasyTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FantasyTransaction
        fields = [
            "id", "league_id", "uuid", "scoring_period_id",
            "type", "status", "team_espn_id", "bid_amount",
            "waiver_priority", "process_date", "proposed_date",
            "items", "created_at", "updated_at",
        ]
