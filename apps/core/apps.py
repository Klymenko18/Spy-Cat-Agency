from django.apps import AppConfig
from pathlib import Path

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    path = str(Path(__file__).resolve().parent)
