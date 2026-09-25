"""Production-only settings for the Erizon Django application.

The development settings stay in ``amazon.settings``. Set
``DJANGO_SETTINGS_MODULE=amazon.production_settings`` in the service
environment to use this module on the server.
"""

import os

from django.core.exceptions import ImproperlyConfigured

from .settings import *  # noqa: F403


def _get_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _get_csv(name: str) -> list[str]:
    return [value.strip() for value in os.getenv(name, "").split(",") if value.strip()]


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set in production.")

DEBUG = False

ALLOWED_HOSTS = _get_csv("DJANGO_ALLOWED_HOSTS")
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS must be set in production.")

CSRF_TRUSTED_ORIGINS = _get_csv("DJANGO_CSRF_TRUSTED_ORIGINS")

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405

# The reverse proxy runs locally. HTTPS-related flags deliberately remain
# configurable because the initial parallel deployment is served on a raw IP
# and port; enable them once a TLS hostname is configured.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = _get_bool("DJANGO_SECURE_SSL_REDIRECT")
SESSION_COOKIE_SECURE = _get_bool("DJANGO_SESSION_COOKIE_SECURE")
CSRF_COOKIE_SECURE = _get_bool("DJANGO_CSRF_COOKIE_SECURE")
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
