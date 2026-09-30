from rest_framework.test import APIRequestFactory

from apps.ingest.views import IngestionView


def test_anonymous_ingestion_denied(settings):
    settings.INGEST_REQUIRE_STAFF = True
    response = IngestionView.as_view()(APIRequestFactory().post("/"))
    assert response.status_code in (401, 403)
