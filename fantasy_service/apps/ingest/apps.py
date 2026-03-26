"""Ingest app configuration."""

from django.apps import AppConfig


class IngestConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ingest"
    verbose_name = "Data Ingestion"
