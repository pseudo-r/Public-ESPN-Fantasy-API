"""Deployment settings; secrets and database/cache URLs come from the environment."""
from .base import *  # noqa: F401, F403

DEBUG = False
CELERY_TASK_ALWAYS_EAGER = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
