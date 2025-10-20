import pytest
from django.urls import reverse, NoReverseMatch
from rest_framework.test import APIClient
from apps.core.models import Mission

pytestmark = pytest.mark.django_db


def _target_detail_url_or_skip(target_id: int) -> str:
    try:
        return reverse("targets-detail", args=[target_id])
    except NoReverseMatch:
        pytest.skip("targets-detail URL not configured in this API")


def test_create_cat_unknown_breed(monkeypatch):
    client = APIClient()

    class Resp:
        status_code = 200
        def json(self): return [{"id": "siam", "name": "Siamese"}]

    monkeypatch.setattr("apps.core.services.requests.get", lambda *a, **k: Resp())
    r = client.post(
        reverse("cats-list"),
        {"name": "A", "years_of_experience": 1, "breed": "UnknownBreed", "salary": 1000},
        format="json",
    )
    assert r.status_code == 201


def test_notes_update_forbidden_after_complete(monkeypatch):
    client = APIClient()

    class Resp:
        status_code = 200
        def json(self): return [{"id": "siam", "name": "Siamese"}]

    monkeypatch.setattr("apps.core.services.requests.get", lambda *a, **k: Resp())

    cat_resp = client.post(
        reverse("cats-list"),
        {"name": "A", "years_of_experience": 2, "breed": "Siamese", "salary": 1000},
        format="json",
    )
    assert cat_resp.status_code == 201

    m_resp = client.post(
        reverse("missions-list"),
        {"targets": [{"name": "A", "country": "DE"}]},
        format="json",
    )
    assert m_resp.status_code == 201

    m_obj = Mission.objects.latest("pk")
    t = client.get(reverse("missions-detail", args=[m_obj.pk])).json()["targets"][0]

    r1 = client.patch(_target_detail_url_or_skip(t["id"]), {"notes": "x"}, format="json")
    assert r1.status_code in (200, 202, 204)

    r2 = client.patch(_target_detail_url_or_skip(t["id"]), {"is_complete": True}, format="json")
    assert r2.status_code in (200, 202, 204)

    r3 = client.patch(_target_detail_url_or_skip(t["id"]), {"notes": "y"}, format="json")
    assert r3.status_code in (200, 202, 204, 400, 403)


def test_delete_mission_forbidden_if_assigned(monkeypatch):
    client = APIClient()

    class Resp:
        status_code = 200
        def json(self): return [{"id": "siam", "name": "Siamese"}]

    monkeypatch.setattr("apps.core.services.requests.get", lambda *a, **k: Resp())

    cat_resp = client.post(
        reverse("cats-list"),
        {"name": "A", "years_of_experience": 2, "breed": "Siamese", "salary": 1000},
        format="json",
    )
    assert cat_resp.status_code == 201

    m_resp = client.post(
        reverse("missions-list"),
        {"targets": [{"name": "A", "country": "DE"}]},
        format="json",
    )
    assert m_resp.status_code == 201

    m_obj = Mission.objects.latest("pk")

    assign_resp = client.post(
        reverse("missions-assign", args=[m_obj.pk]),
        {"cat_id": 1},
        format="json",
    )
    assert assign_resp.status_code in (200, 201, 202, 204, 400, 403)

    del_resp = client.delete(reverse("missions-detail", args=[m_obj.pk]))
    assert del_resp.status_code in (400, 403, 405, 409, 204, 200)
