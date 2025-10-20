from functools import lru_cache
from typing import Set
import requests
from django.conf import settings

BREEDS_URL = "https://api.thecatapi.com/v1/breeds"


@lru_cache(maxsize=1)
def _breeds_set() -> Set[str]:
    headers = {}
    if settings.THECATAPI_API_KEY:
        headers["x-api-key"] = settings.THECATAPI_API_KEY
    try:
        resp = requests.get(BREEDS_URL, headers=headers, timeout=5)
        if resp.status_code != 200:
            return set()
        data = resp.json()
        names = {str(b.get("name", "")).strip().lower() for b in data}
        ids = {str(b.get("id", "")).strip().lower() for b in data}
        return {x for x in names | ids if x}
    except Exception:
        return set()


def clear_breeds_cache() -> None:
    _breeds_set.cache_clear()  


def is_valid_breed(value: str) -> bool:
    norm = (value or "").strip().lower()
    if not norm:
        return False
    return norm in _breeds_set()
