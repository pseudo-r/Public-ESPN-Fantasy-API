"""Test settings."""

import os as _os

import environ as _environ

_os.environ.setdefault("SECRET_KEY", "test-only-not-production")
_os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
_os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
_os.environ.setdefault("ESPN_S2", "")
_os.environ.setdefault("SWID", "")

from .base import *  # noqa: E402, F401, F403

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

# Opt into a separate test database explicitly; never use production DATABASE_URL.


if _os.environ.get("TEST_DATABASE_URL"):
    DATABASES = {"default": _environ.Env.db_url_config(_os.environ["TEST_DATABASE_URL"])}
MIDDLEWARE = [m for m in MIDDLEWARE if m != "whitenoise.middleware.WhiteNoiseMiddleware"]  # noqa: F405
INGEST_REQUIRE_STAFF = False

CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
