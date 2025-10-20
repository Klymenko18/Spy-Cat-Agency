from .base import *

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }
}

REST_FRAMEWORK = REST_FRAMEWORK

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "sca-test-cache",
        "TIMEOUT": 60,
    }
}

THECATAPI_API_KEY = ""
