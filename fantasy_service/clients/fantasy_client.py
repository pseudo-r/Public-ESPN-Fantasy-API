"""ESPN Fantasy API HTTP client.

Wraps the lm-api-reads.fantasy.espn.com Fantasy v3 API.
Handles cookie auth, retry logic, X-Fantasy-Filter header construction,
and the pre-2018 leagueHistory URL fallback.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

import httpx
import structlog
from django.conf import settings
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://lm-api-reads.fantasy.espn.com/apis/v3/games"
GAME_CODES = {"ffl", "fba", "flb", "fhl"}

GAME_NAMES = {
    "ffl": "Fantasy Football",
    "fba": "Fantasy Basketball",
    "flb": "Fantasy Baseball",
    "fhl": "Fantasy Hockey",
}

DEFAULT_HEADERS = {
    "Accept": "application/json",
    "Referer": "https://fantasy.espn.com/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
}


# ---------------------------------------------------------------------------
# Response wrapper
# ---------------------------------------------------------------------------

@dataclass
class FantasyResponse:
    """Wrapper around a parsed ESPN Fantasy API response."""

    data: dict[str, Any] | list[Any]
    status_code: int
    url: str

    @property
    def list_data(self) -> list[Any]:
        """Return data coerced to list (pre-2018 endpoints return arrays)."""
        if isinstance(self.data, list):
            return self.data
        return [self.data]

    @property
    def league_data(self) -> dict[str, Any]:
        """Return the single league object, unwrapping array if needed."""
        if isinstance(self.data, list):
            return self.data[0] if self.data else {}
        return self.data


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class FantasyAPIError(Exception):
    """Raised when the ESPN Fantasy API returns an unexpected response."""


class FantasyAuthError(FantasyAPIError):
    """Raised on 401 — league is private or credentials are invalid."""


class FantasyNotFoundError(FantasyAPIError):
    """Raised on 404 — league or resource does not exist."""


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

@dataclass
class FantasyClient:
    """ESPN Fantasy API client.

    Usage:
        client = FantasyClient()
        data = client.get_league("ffl", 2025, 336358, views=["mSettings", "mTeam"])
    """

    espn_s2: str = field(default_factory=lambda: getattr(settings, "ESPN_S2", ""))
    swid: str = field(default_factory=lambda: getattr(settings, "SWID", ""))
    request_delay_ms: int = field(
        default_factory=lambda: getattr(settings, "ESPN_REQUEST_DELAY_MS", 300)
    )
    timeout: float = 30.0

    def _cookies(self) -> dict[str, str]:
        cookies: dict[str, str] = {}
        if self.espn_s2:
            cookies["espn_s2"] = self.espn_s2
        if self.swid:
            cookies["SWID"] = self.swid
        return cookies

    def _league_url(self, game_code: str, season: int, league_id: int, historical: bool = False) -> str:
        if historical:
            return f"{BASE_URL}/{game_code}/leagueHistory/{league_id}?seasonId={season}"
        return f"{BASE_URL}/{game_code}/seasons/{season}/segments/0/leagues/{league_id}"

    def _check_html_redirect(self, text: str, url: str) -> None:
        """ESPN sometimes returns HTML instead of JSON when bot-detection triggers."""
        if text.strip().startswith("<!DOCTYPE html") or text.strip().startswith("<html"):
            raise FantasyAPIError(
                f"Received HTML redirect instead of JSON from {url}. "
                "Add browser-like headers or switch to lm-api-reads subdomain."
            )

    @retry(
        retry=retry_if_exception_type(FantasyAPIError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def _get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> FantasyResponse:
        """Raw GET with retry, HTML detection, and rate-limiting."""
        merged_headers = {**DEFAULT_HEADERS, **(headers or {})}

        if self.request_delay_ms > 0:
            time.sleep(self.request_delay_ms / 1000)

        logger.debug("fantasy_api_request", url=url, params=params)

        try:
            with httpx.Client(timeout=self.timeout) as client:
                r = client.get(
                    url,
                    params=params,
                    headers=merged_headers,
                    cookies=self._cookies(),
                )
        except httpx.RequestError as exc:
            raise FantasyAPIError(f"Network error fetching {url}: {exc}") from exc

        logger.debug("fantasy_api_response", url=url, status=r.status_code)

        if r.status_code == 401:
            raise FantasyAuthError(
                f"401 Unauthorized for {url}. "
                "League may be private — provide ESPN_S2 and SWID credentials."
            )

        if r.status_code == 404:
            raise FantasyNotFoundError(f"404 Not Found: {url}")

        if r.status_code != 200:
            raise FantasyAPIError(f"ESPN Fantasy API returned HTTP {r.status_code} for {url}")

        self._check_html_redirect(r.text, url)

        return FantasyResponse(data=r.json(), status_code=r.status_code, url=url)

    # -----------------------------------------------------------------------
    # League endpoint (main data hub)
    # -----------------------------------------------------------------------

    def get_league(
        self,
        game_code: str,
        season: int,
        league_id: int,
        views: list[str],
        scoring_period_id: int | None = None,
        matchup_period_id: int | None = None,
    ) -> FantasyResponse:
        """Fetch league data for one or more views.

        Automatically falls back to the leagueHistory URL if the modern
        endpoint returns 401 (pre-2018 season behaviour).
        """
        url = self._league_url(game_code, season, league_id)
        params: dict[str, Any] = {"view": views}
        if scoring_period_id is not None:
            params["scoringPeriodId"] = scoring_period_id
        if matchup_period_id is not None:
            params["matchupPeriodId"] = matchup_period_id

        try:
            return self._get(url, params=params)
        except FantasyAuthError:
            if season < 2018:
                logger.info(
                    "falling_back_to_league_history",
                    game_code=game_code,
                    season=season,
                    league_id=league_id,
                )
                hist_url = self._league_url(game_code, season, league_id, historical=True)
                # seasonId already embedded in leagueHistory URL; rebuild params without it
                hist_params: dict[str, Any] = {"view": views}
                if scoring_period_id is not None:
                    hist_params["scoringPeriodId"] = scoring_period_id
                return self._get(hist_url, params=hist_params)
            raise

    # -----------------------------------------------------------------------
    # Player pool endpoint (different URL pattern)
    # -----------------------------------------------------------------------

    def get_pro_players(self, game_code: str, season: int) -> FantasyResponse:
        """Fetch all active professional players for a sport/season.

        Endpoint: /apis/v3/games/{game_code}/seasons/{season}/players?view=players_wl
        """
        url = f"{BASE_URL}/{game_code}/seasons/{season}/players"
        headers = {"X-Fantasy-Filter": json.dumps({"filterActive": {"value": True}})}
        return self._get(url, params={"view": "players_wl"}, headers=headers)

    def get_player_pool(
        self,
        game_code: str,
        season: int,
        league_id: int,
        limit: int = 300,
        offset: int = 0,
        status_filter: list[str] | None = None,
        slot_ids: list[int] | None = None,
        scoring_period_id: int | None = None,
    ) -> FantasyResponse:
        """Fetch filtered player pool using kona_player_info view."""
        url = self._league_url(game_code, season, league_id)
        params: dict[str, Any] = {"view": "kona_player_info"}
        if scoring_period_id is not None:
            params["scoringPeriodId"] = scoring_period_id

        player_filter: dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "sortPercOwned": {"sortPriority": 1, "sortAsc": False},
        }
        if status_filter:
            player_filter["filterStatus"] = {"value": status_filter}
        if slot_ids:
            player_filter["filterSlotIds"] = {"value": slot_ids}

        headers = {"X-Fantasy-Filter": json.dumps({"players": player_filter})}
        return self._get(url, params=params, headers=headers)

    def get_player_card(
        self,
        game_code: str,
        season: int,
        league_id: int,
        player_ids: list[int],
        top_scoring_periods: int = 5,
    ) -> FantasyResponse:
        """Fetch per-player deep stat cards using kona_playercard view."""
        url = self._league_url(game_code, season, league_id)
        additional_value = [f"00{season}", f"10{season}"]
        player_filter = {
            "players": {
                "filterIds": {"value": player_ids},
                "filterStatsForTopScoringPeriodIds": {
                    "value": top_scoring_periods,
                    "additionalValue": additional_value,
                },
            }
        }
        headers = {"X-Fantasy-Filter": json.dumps(player_filter)}
        return self._get(url, params={"view": "kona_playercard"}, headers=headers)

    # -----------------------------------------------------------------------
    # Player news endpoint (different URL pattern)
    # -----------------------------------------------------------------------

    def get_player_news(self, game_code: str, season: int, player_id: int) -> FantasyResponse:
        """Fetch news items for a specific player.

        Endpoint: /apis/v3/games/{game_code}/news/players?playerId={id}
        """
        url = f"{BASE_URL}/{game_code}/news/players"
        return self._get(url, params={"playerId": player_id, "seasonId": season})

    # -----------------------------------------------------------------------
    # Message board endpoint (uses /communication sub-path)
    # -----------------------------------------------------------------------

    def get_message_board(
        self,
        game_code: str,
        season: int,
        league_id: int,
        msg_types: list[str] | None = None,
    ) -> FantasyResponse:
        """Fetch league message board threads."""
        url = (
            f"{BASE_URL}/{game_code}/seasons/{season}/segments/0"
            f"/leagues/{league_id}/communication"
        )
        headers: dict[str, str] = {}
        if msg_types:
            topic_filter: dict[str, Any] = {}
            for t in msg_types:
                topic_filter[t] = {"sortMessageDate": {"sortPriority": 1, "sortAsc": False}}
            headers["X-Fantasy-Filter"] = json.dumps({"topicsByType": topic_filter})
        return self._get(url, params={"view": "kona_league_messageboard"}, headers=headers)

    # -----------------------------------------------------------------------
    # Convenience: game metadata
    # -----------------------------------------------------------------------

    def get_game_metadata(self, game_code: str) -> FantasyResponse:
        """Fetch game-level metadata (current season, sport name, etc).

        Endpoint: /apis/v3/games/{game_code}
        """
        url = f"{BASE_URL}/{game_code}"
        return self._get(url)


def get_fantasy_client() -> FantasyClient:
    """Factory: return a configured FantasyClient from Django settings."""
    return FantasyClient(
        espn_s2=getattr(settings, "ESPN_S2", ""),
        swid=getattr(settings, "SWID", ""),
        request_delay_ms=getattr(settings, "ESPN_REQUEST_DELAY_MS", 300),
    )
