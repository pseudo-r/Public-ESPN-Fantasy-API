"""Test settings."""

from .base import *  # noqa: F401, F403

SECRET_KEY = "test-secret-key"
DEBUG = False
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
ESPN_S2 = "test_s2"
SWID = "{TEST-SWID}"
