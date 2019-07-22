import os
from datetime import time
from decimal import Decimal

import dj_database_url
import django_heroku
from django.conf.global_settings import DATETIME_INPUT_FORMATS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# TODO: env vars
FEES = {
    "standard": {
        "charge": Decimal(0.36),
        "charge_per_minute": Decimal(0.09),
        "starts_at": time(6, 0, 0),
        "ends_at": time(21, 59, 59),
    },
    "reduced": {
        "charge": Decimal(0.36),
        "charge_per_minute": Decimal(0.00),
        "starts_at": time(22, 0, 0),
        "ends_at": time(5, 59, 59),
    },
}

DATETIME_INPUT_FORMATS += ("%Y-%m-%dT%H:%M:%SZ",)


SECRET_KEY = "14s$-%b8x%k!p3ah-mleqb#80esw*sfxxn@kgqyk9g=e*yvl8$"

DEBUG = False


INSTALLED_APPS = [
    "django.contrib.contenttypes",
    # Our apps
    "calls.apps.CallsConfig",
    "reports.apps.ReportsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "bell.urls"

TEMPLATES = []

WSGI_APPLICATION = "bell.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = False
USE_TZ = True

DATABASES["default"].update(dj_database_url.config(conn_max_age=500, ssl_require=True))

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

ALLOWED_HOSTS = ["*"]

STATIC_ROOT = os.path.join(PROJECT_ROOT, "staticfiles")
STATIC_URL = "/static/"

STATICFILES_DIRS = [os.path.join(PROJECT_ROOT, "static")]


django_heroku.settings(locals())
