"""Fantasy app configuration."""

from django.apps import AppConfig


class FantasyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.fantasy"
    verbose_name = "ESPN Fantasy"
