"""URL routing for the fantasy app."""

from rest_framework.routers import DefaultRouter

from apps.fantasy.views import (
    DraftPickViewSet,
    FantasyGameViewSet,
    FantasyLeagueViewSet,
    FantasyPlayerViewSet,
    FantasyTeamViewSet,
    FantasyTransactionViewSet,
    MatchupViewSet,
    RosterEntryViewSet,
)

router = DefaultRouter()
router.register(r"games", FantasyGameViewSet, basename="fantasygame")
router.register(r"leagues", FantasyLeagueViewSet, basename="fantasyleague")
router.register(r"teams", FantasyTeamViewSet, basename="fantasyteam")
router.register(r"players", FantasyPlayerViewSet, basename="fantasyplayer")
router.register(r"roster", RosterEntryViewSet, basename="rosterentry")
router.register(r"matchups", MatchupViewSet, basename="matchup")
router.register(r"draft", DraftPickViewSet, basename="draftpick")
router.register(r"transactions", FantasyTransactionViewSet, basename="fantasytransaction")

urlpatterns = router.urls
