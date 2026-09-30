import pytest

from clients.fantasy_client import FantasyAPIError, FantasyClient


@pytest.mark.parametrize("method,suffix", [("get_season", ""), ("get_pro_schedule", "?view=proTeamSchedules_wl")])
def test_metadata_routes(httpx_mock, method, suffix):
    httpx_mock.add_response(url="https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2026" + suffix, json={"settings": {}})
    client = FantasyClient(request_delay_ms=0)
    assert getattr(client, method)("ffl", 2026).data == {"settings": {}}

@pytest.mark.parametrize("status", [400, 401, 403, 404, 429])
def test_terminal_errors_once(httpx_mock, status):
    httpx_mock.add_response(status_code=status)
    with pytest.raises(FantasyAPIError):
        FantasyClient(request_delay_ms=0).get_season("ffl", 2026)
    assert len(httpx_mock.get_requests()) == 1
