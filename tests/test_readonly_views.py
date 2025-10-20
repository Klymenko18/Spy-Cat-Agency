import pytest
from django.urls import reverse
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

def test_missions_list_empty_then_nonempty():
    c = APIClient()
    r = c.get(reverse("missions-list"))
    assert r.status_code == 200 and r.json() == []
    c.post(reverse("missions-list"), {"targets":[{"name":"A","country":"DE"}]}, format="json")
    r = c.get(reverse("missions-list"))
    assert r.status_code == 200 and len(r.json()) == 1
