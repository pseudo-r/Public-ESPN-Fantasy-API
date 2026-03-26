"""Database models for ESPN Fantasy sports data."""

from django.db import models


class TimestampMixin(models.Model):
    """Mixin providing created_at and updated_at timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class FantasyGame(TimestampMixin):
    """ESPN Fantasy game type (sport/platform combination)."""

    GAME_CODE_CHOICES = [
        ("ffl", "Fantasy Football"),
        ("fba", "Fantasy Basketball"),
        ("flb", "Fantasy Baseball"),
        ("fhl", "Fantasy Hockey"),
    ]

    game_code = models.CharField(max_length=10, unique=True, db_index=True, choices=GAME_CODE_CHOICES)
    name = models.CharField(max_length=100)
    pro_sport_name = models.CharField(max_length=50, blank=True)
    current_season_id = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    raw_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["game_code"]

    def __str__(self) -> str:
        return f"{self.name} ({self.game_code})"


class FantasyLeague(TimestampMixin):
    """A user's ESPN Fantasy league for a specific season."""

    game = models.ForeignKey(FantasyGame, on_delete=models.CASCADE, related_name="leagues")
    espn_id = models.PositiveIntegerField(db_index=True)
    season_id = models.PositiveIntegerField(db_index=True)
    name = models.CharField(max_length=200)
    size = models.PositiveSmallIntegerField(default=0)
    is_public = models.BooleanField(default=True)
    current_scoring_period_id = models.PositiveIntegerField(default=1)
    current_matchup_period = models.PositiveIntegerField(default=1)
    first_scoring_period = models.PositiveIntegerField(default=1)
    final_scoring_period = models.PositiveIntegerField(default=1)
    draft_completed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_expired = models.BooleanField(default=False)

    SCORING_TYPE_CHOICES = [
        ("H2H_POINTS", "Head-to-Head Points"),
        ("H2H_CATEGORY", "Head-to-Head Categories"),
        ("ROTO", "Rotisserie"),
        ("POINTS", "Total Points"),
    ]
    scoring_type = models.CharField(max_length=30, blank=True, choices=SCORING_TYPE_CHOICES)
    acquisition_type = models.CharField(max_length=30, blank=True)
    draft_type = models.CharField(max_length=20, blank=True)
    playoff_team_count = models.PositiveSmallIntegerField(default=4)
    matchup_period_count = models.PositiveSmallIntegerField(default=0)

    # Full raw settings for extensibility
    raw_settings = models.JSONField(default=dict, blank=True)
    raw_status = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-season_id", "name"]
        unique_together = [["game", "espn_id", "season_id"]]

    def __str__(self) -> str:
        return f"{self.name} ({self.game.game_code.upper()} {self.season_id})"

    @property
    def game_code(self) -> str:
        return self.game.game_code


class FantasyMember(TimestampMixin):
    """A league member (owner)."""

    league = models.ForeignKey(FantasyLeague, on_delete=models.CASCADE, related_name="members")
    swid = models.CharField(max_length=100, db_index=True)
    display_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_league_manager = models.BooleanField(default=False)

    class Meta:
        ordering = ["display_name"]
        unique_together = [["league", "swid"]]

    def __str__(self) -> str:
        return f"{self.display_name} ({self.league})"


class FantasyTeam(TimestampMixin):
    """A fantasy team within a league."""

    league = models.ForeignKey(FantasyLeague, on_delete=models.CASCADE, related_name="teams")
    espn_id = models.PositiveIntegerField(db_index=True)
    name = models.CharField(max_length=200)
    abbrev = models.CharField(max_length=20, blank=True)
    division_id = models.PositiveSmallIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    ties = models.PositiveIntegerField(default=0)
    points_for = models.FloatField(default=0.0)
    points_against = models.FloatField(default=0.0)
    standing = models.PositiveSmallIntegerField(default=0)
    waiver_rank = models.PositiveSmallIntegerField(default=0)
    total_acquisitions = models.PositiveIntegerField(default=0)
    total_trades = models.PositiveIntegerField(default=0)
    # Array of owner SWIDs
    owner_swids = models.JSONField(default=list, blank=True)
    raw_record = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["standing", "name"]
        unique_together = [["league", "espn_id"]]

    def __str__(self) -> str:
        return f"{self.name} ({self.league})"

    @property
    def record(self) -> str:
        return f"{self.wins}-{self.losses}-{self.ties}"


class FantasyPlayer(TimestampMixin):
    """A professional player in the ESPN player pool."""

    espn_id = models.PositiveIntegerField(unique=True, db_index=True)
    full_name = models.CharField(max_length=150, db_index=True)
    first_name = models.CharField(max_length=75, blank=True)
    last_name = models.CharField(max_length=75, blank=True)
    pro_team_id = models.PositiveIntegerField(default=0)
    default_position_id = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_droppable = models.BooleanField(default=True)

    INJURY_STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("QUESTIONABLE", "Questionable"),
        ("DOUBTFUL", "Doubtful"),
        ("OUT", "Out"),
        ("INJURY_RESERVE", "Injury Reserve"),
        ("SUSPENDED", "Suspended"),
        ("BEREAVEMENT", "Bereavement"),
    ]
    injury_status = models.CharField(max_length=30, default="ACTIVE", choices=INJURY_STATUS_CHOICES, db_index=True)
    percent_owned = models.FloatField(default=0.0)
    percent_started = models.FloatField(default=0.0)
    avg_draft_position = models.FloatField(default=0.0)
    eligible_slots = models.JSONField(default=list, blank=True)
    raw_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-percent_owned"]

    def __str__(self) -> str:
        return f"{self.full_name} (ESPN #{self.espn_id})"


class RosterEntry(TimestampMixin):
    """A player on a fantasy team's roster for a specific scoring period."""

    team = models.ForeignKey(FantasyTeam, on_delete=models.CASCADE, related_name="roster_entries")
    player = models.ForeignKey(FantasyPlayer, on_delete=models.CASCADE, related_name="roster_entries")
    scoring_period_id = models.PositiveIntegerField(db_index=True)
    lineup_slot_id = models.PositiveSmallIntegerField(default=0)

    ACQUISITION_TYPE_CHOICES = [
        ("DRAFT", "Draft"),
        ("WAIVER", "Waiver"),
        ("FREE_AGENT", "Free Agent"),
        ("TRADE", "Trade"),
    ]
    acquisition_type = models.CharField(max_length=20, blank=True, choices=ACQUISITION_TYPE_CHOICES)
    acquisition_date = models.DateTimeField(null=True, blank=True)
    applied_stat_total = models.FloatField(default=0.0)
    injury_status = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["lineup_slot_id"]
        unique_together = [["team", "player", "scoring_period_id"]]

    def __str__(self) -> str:
        return f"{self.player.full_name} → {self.team.name} (period {self.scoring_period_id})"


class Matchup(TimestampMixin):
    """A head-to-head matchup between two fantasy teams."""

    league = models.ForeignKey(FantasyLeague, on_delete=models.CASCADE, related_name="matchups")
    espn_id = models.PositiveIntegerField(db_index=True)
    matchup_period_id = models.PositiveIntegerField(db_index=True)
    home_team = models.ForeignKey(
        FantasyTeam, on_delete=models.CASCADE, related_name="home_matchups", null=True, blank=True
    )
    away_team = models.ForeignKey(
        FantasyTeam, on_delete=models.CASCADE, related_name="away_matchups", null=True, blank=True
    )
    home_points = models.FloatField(default=0.0)
    away_points = models.FloatField(default=0.0)
    home_projected_points = models.FloatField(default=0.0)
    away_projected_points = models.FloatField(default=0.0)

    WINNER_CHOICES = [
        ("HOME", "Home"),
        ("AWAY", "Away"),
        ("UNDECIDED", "Undecided"),
        ("NONE_YET", "Not Started"),
    ]
    winner = models.CharField(max_length=20, default="UNDECIDED", choices=WINNER_CHOICES)

    PLAYOFF_TIER_CHOICES = [
        ("NONE", "Regular Season"),
        ("WINNERS_BRACKET", "Winners Bracket"),
        ("LOSERS_BRACKET", "Losers Bracket"),
        ("CONSOLATION", "Consolation"),
        ("TOILET_BOWL", "Toilet Bowl"),
    ]
    playoff_tier_type = models.CharField(max_length=20, default="NONE", choices=PLAYOFF_TIER_CHOICES)
    is_playoff = models.BooleanField(default=False)

    class Meta:
        ordering = ["matchup_period_id", "espn_id"]
        unique_together = [["league", "espn_id"]]

    def __str__(self) -> str:
        home = self.home_team.name if self.home_team else "?"
        away = self.away_team.name if self.away_team else "?"
        return f"{away} @ {home} — Period {self.matchup_period_id}"


class DraftPick(TimestampMixin):
    """A single pick from a fantasy league draft."""

    league = models.ForeignKey(FantasyLeague, on_delete=models.CASCADE, related_name="draft_picks")
    team = models.ForeignKey(
        FantasyTeam, on_delete=models.CASCADE, related_name="draft_picks", null=True, blank=True
    )
    nominating_team = models.ForeignKey(
        FantasyTeam,
        on_delete=models.SET_NULL,
        related_name="nominated_picks",
        null=True,
        blank=True,
        help_text="Auction only: team that nominated this player",
    )
    player_espn_id = models.PositiveIntegerField(db_index=True)
    player_name = models.CharField(max_length=150, blank=True)
    overall_pick = models.PositiveSmallIntegerField()
    round_id = models.PositiveSmallIntegerField()
    round_pick = models.PositiveSmallIntegerField()
    bid_amount = models.PositiveIntegerField(default=0)
    auto_drafted = models.BooleanField(default=False)
    keeper = models.BooleanField(default=False)

    class Meta:
        ordering = ["overall_pick"]
        unique_together = [["league", "overall_pick"]]

    def __str__(self) -> str:
        return f"Pick #{self.overall_pick}: {self.player_name or self.player_espn_id}"


class FantasyTransaction(TimestampMixin):
    """A waiver claim, free agent add, drop, or trade in a fantasy league."""

    league = models.ForeignKey(FantasyLeague, on_delete=models.CASCADE, related_name="transactions")
    uuid = models.CharField(max_length=100, db_index=True)
    scoring_period_id = models.PositiveIntegerField(db_index=True)

    TYPE_CHOICES = [
        ("WAIVER", "Waiver Claim"),
        ("FREE_AGENT", "Free Agent Add"),
        ("TRADE", "Trade"),
        ("DRAFT", "Draft Pick"),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, db_index=True)

    STATUS_CHOICES = [
        ("EXECUTED", "Executed"),
        ("CANCELED", "Canceled"),
        ("PENDING", "Pending"),
        ("VETOED", "Vetoed"),
        ("FAILED", "Failed"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, db_index=True)

    team_espn_id = models.PositiveIntegerField(default=0)
    bid_amount = models.PositiveIntegerField(default=0)
    waiver_priority = models.PositiveSmallIntegerField(default=0)
    process_date = models.DateTimeField(null=True, blank=True)
    proposed_date = models.DateTimeField(null=True, blank=True)
    # Array of {playerId, type, fromTeamId, toTeamId}
    items = models.JSONField(default=list, blank=True)
    raw_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-process_date"]
        unique_together = [["league", "uuid"]]

    def __str__(self) -> str:
        return f"{self.type} ({self.status}) — Period {self.scoring_period_id}"
