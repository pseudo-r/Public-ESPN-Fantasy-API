"""URL routing for the ingest app."""

from django.urls import path

from apps.ingest.views import (
    IngestLeagueView,
    IngestPlayersView,
    IngestRosterView,
    IngestTransactionsView,
)

urlpatterns = [
    path("league/", IngestLeagueView.as_view(), name="ingest-league"),
    path("roster/", IngestRosterView.as_view(), name="ingest-roster"),
    path("players/", IngestPlayersView.as_view(), name="ingest-players"),
    path("transactions/", IngestTransactionsView.as_view(), name="ingest-transactions"),
]
