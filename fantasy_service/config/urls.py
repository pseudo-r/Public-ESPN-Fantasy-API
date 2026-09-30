"""Root URL configuration."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.core.upstream import UpstreamView

urlpatterns = [
    path("api/v1/live/<str:game_code>/<int:season>/", UpstreamView.as_view(client_method="get_season"), name="live-get_season"),
    path("api/v1/live/<str:game_code>/<int:season>/pro-schedule/", UpstreamView.as_view(client_method="get_pro_schedule"), name="live-get_pro_schedule"),

    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/fantasy/", include("apps.fantasy.urls")),
    path("api/v1/ingest/", include("apps.ingest.urls")),
]
