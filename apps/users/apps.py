from django.apps import AppConfig
from pathlib import Path

class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
    path = str(Path(__file__).resolve().parent)
