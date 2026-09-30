"""Explicit read-only proxy routes for additional upstream resources."""
from contextlib import nullcontext

import httpx
from rest_framework.response import Response
from rest_framework.views import APIView

from clients.fantasy_client import FantasyAPIError, FantasyClient


class UpstreamView(APIView):
    client_method = "get_season"

    def get(self, request, **kwargs):  # noqa: ARG002
        try:
            with nullcontext(FantasyClient()) as client:
                result = getattr(client, self.client_method)(**kwargs)
                return Response(result.data if hasattr(result, "data") else result)
        except httpx.HTTPStatusError as exc:
            code = exc.response.status_code
            return Response({"detail": "Upstream request failed", "upstream_status": code},
                            status=404 if code == 404 else 502)
        except (httpx.RequestError, ValueError, FantasyAPIError):
            return Response({"detail": "Upstream unavailable or invalid response"}, status=502)
