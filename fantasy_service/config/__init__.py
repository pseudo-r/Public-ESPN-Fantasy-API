"""Config package. Import Celery app so tasks are registered."""
from .celery import app as celery_app

__all__ = ["celery_app"]
