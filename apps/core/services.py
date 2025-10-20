import requests
from django.core.cache import cache
from django.conf import settings

BREEDS_CACHE_KEY = "thecatapi_breeds_v1"

def is_valid_breed(breed_name: str) -> bool:
    name = (breed_name or "").strip().lower()
    if not name:
        return False
    breeds = cache.get(BREEDS_CACHE_KEY)
    if breeds is None:
        headers = {}
        if settings.THECATAPI_API_KEY:
            headers["x-api-key"] = settings.THECATAPI_API_KEY
        resp = requests.get("https://api.thecatapi.com/v1/breeds", headers=headers, timeout=10)
        if resp.status_code != 200:
            return False
        breeds = resp.json()
        cache.set(BREEDS_CACHE_KEY, breeds, timeout=None)
    names = {b.get("name", "").strip().lower() for b in breeds}
    ids = {b.get("id", "").strip().lower() for b in breeds}
    return name in names or name in ids
