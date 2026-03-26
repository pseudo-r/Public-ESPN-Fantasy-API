"""Local development settings."""

import environ

from .base import *  # noqa: F401, F403

env = environ.Env()
environ.Env.read_env()

SECRET_KEY = env("SECRET_KEY", default="local-dev-secret-key-not-for-production")
DEBUG = True
ALLOWED_HOSTS = ["*"]
CELERY_TASK_ALWAYS_EAGER = True  # Run tasks synchronously in dev
