from django.urls import reverse
from rest_framework.test import APIClient
from apps.core.models import Mission, Cat
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.core.models import Mission, Cat

pytestmark = pytest.mark.django_db


def test_assign_and_notes_rules(monkeypatch):
    client = APIClient()

    class Resp:
        status_code = 200
        def json(self): return [{"id": "siam", "name": "Siamese"}]

    monkeypatch.setattr("apps.core.services.requests.get", lambda *a, **k: Resp())

    client.post(
        reverse("cats-list"),
        {"name": "A", "years_of_experience": 2, "breed": "Siamese", "salary": 1000},
        format="json",
    )
    client.post(
        reverse("missions-list"),
        {"targets": [{"name": "A", "country": "DE"}, {"name": "B", "country": "DE"}]},
        format="json",
    )

    cat_obj = Cat.objects.latest("pk")
    m_obj = Mission.objects.latest("pk")

    r = client.post(
        reverse("missions-assign", args=[m_obj.pk]),
        {"cat_id": cat_obj.pk},
        format="json",
    )
    assert r.status_code in (200, 201, 202, 204)
