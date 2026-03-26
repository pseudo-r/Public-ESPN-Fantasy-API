"""Django admin for ESPN Fantasy models."""

from django.contrib import admin

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


@admin.register(FantasyGame)
class FantasyGameAdmin(admin.ModelAdmin):
    list_display = ["game_code", "name", "current_season_id", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["game_code", "name"]


@admin.register(FantasyLeague)
class FantasyLeagueAdmin(admin.ModelAdmin):
    list_display = ["name", "game", "espn_id", "season_id", "size", "is_public", "draft_completed"]
    list_filter = ["game", "is_public", "draft_completed", "scoring_type"]
    search_fields = ["name"]
    ordering = ["-season_id", "name"]
    raw_id_fields: list[str] = []


@admin.register(FantasyMember)
class FantasyMemberAdmin(admin.ModelAdmin):
    list_display = ["display_name", "league", "is_league_manager"]
    list_filter = ["is_league_manager"]
    search_fields = ["display_name", "swid"]


@admin.register(FantasyTeam)
class FantasyTeamAdmin(admin.ModelAdmin):
    list_display = ["name", "abbrev", "league", "standing", "wins", "losses", "ties", "points_for"]
    list_filter = ["league__game"]
    search_fields = ["name", "abbrev"]
    ordering = ["league", "standing"]


@admin.register(FantasyPlayer)
class FantasyPlayerAdmin(admin.ModelAdmin):
    list_display = [
        "full_name", "espn_id", "default_position_id",
        "injury_status", "percent_owned", "is_active",
    ]
    list_filter = ["injury_status", "is_active", "default_position_id"]
    search_fields = ["full_name"]
    ordering = ["-percent_owned"]


@admin.register(RosterEntry)
class RosterEntryAdmin(admin.ModelAdmin):
    list_display = ["player", "team", "scoring_period_id", "lineup_slot_id", "acquisition_type"]
    list_filter = ["acquisition_type"]
    search_fields = ["player__full_name", "team__name"]
    ordering = ["team", "scoring_period_id", "lineup_slot_id"]


@admin.register(Matchup)
class MatchupAdmin(admin.ModelAdmin):
    list_display = ["__str__", "league", "matchup_period_id", "home_points", "away_points", "winner", "is_playoff"]
    list_filter = ["league__game", "winner", "is_playoff", "playoff_tier_type"]
    ordering = ["league", "matchup_period_id"]


@admin.register(DraftPick)
class DraftPickAdmin(admin.ModelAdmin):
    list_display = ["overall_pick", "round_id", "round_pick", "player_name", "team", "bid_amount", "keeper"]
    list_filter = ["keeper", "auto_drafted"]
    search_fields = ["player_name"]
    ordering = ["league", "overall_pick"]


@admin.register(FantasyTransaction)
class FantasyTransactionAdmin(admin.ModelAdmin):
    list_display = ["league", "type", "status", "scoring_period_id", "bid_amount", "process_date"]
    list_filter = ["type", "status"]
    search_fields = ["uuid"]
    ordering = ["-process_date"]
