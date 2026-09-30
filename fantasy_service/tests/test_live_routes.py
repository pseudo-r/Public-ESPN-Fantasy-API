from unittest.mock import MagicMock, patch

import pytest
from rest_framework.test import APIClient


@pytest.mark.parametrize("path,method", [('ffl/2026/', 'get_season'), ('ffl/2026/pro-schedule/', 'get_pro_schedule')])
def test_live_routes(path, method):
    with patch("apps.core.upstream.FantasyClient") as factory:
        client = factory.return_value
        getattr(client, method).return_value = MagicMock(data={"fixture": True})
        response = APIClient().get("/api/v1/live/" + path)
        assert response.status_code == 200
        assert response.json() == {"fixture": True}
        getattr(client, method).assert_called_once()
