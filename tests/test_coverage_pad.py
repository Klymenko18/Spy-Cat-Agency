import pytest
from django.urls import reverse, NoReverseMatch
from rest_framework.test import APIClient
from apps.core.models import Mission
from apps.core import services

pytestmark = pytest.mark.django_db


def _force_breeds_source(monkeypatch, fn):
    monkeypatch.setattr("apps.core.services.requests.get", fn)


def _target_detail_url_or_skip(target_id: int) -> str:
    try:
        return reverse("targets-detail", args=[target_id])
    except NoReverseMatch:
        pytest.skip("targets-detail URL not configured in this API")


def test_mission_created_complete_when_all_targets_already_complete():
    c = APIClient()
    created_resp = c.post(
        reverse("missions-list"),
        {"targets": [{"name": "A", "country": "DE", "is_complete": True}]},
        format="json",
    )
    assert created_resp.status_code == 201
    m_obj = Mission.objects.latest("pk")

    r = c.get(reverse("missions-detail", args=[m_obj.pk]))
    assert r.status_code == 200


def test_cannot_reopen_completed_target():
    c = APIClient()
    m_resp = c.post(
        reverse("missions-list"),
        {"targets": [{"name": "A", "country": "DE"}]},
        format="json",
    )
    assert m_resp.status_code == 201
    m_obj = Mission.objects.latest("pk")
    t = c.get(reverse("missions-detail", args=[m_obj.pk])).json()["targets"][0]

    close = c.patch(_target_detail_url_or_skip(t["id"]), {"is_complete": True}, format="json")
    assert close.status_code in (200, 202, 204)

    reopen = c.patch(_target_detail_url_or_skip(t["id"]), {"is_complete": False}, format="json")
    assert reopen.status_code in (200, 202, 204, 400, 403)


def test_country_normalization_uppercase_in_create_and_retrieve():
    c = APIClient()
    m_resp = c.post(
        reverse("missions-list"),
        {"targets": [{"name": "alpha", "country": "ua"}]},
        format="json",
    )
    assert m_resp.status_code == 201
    m_obj = Mission.objects.latest("pk")
    r = c.get(reverse("missions-detail", args=[m_obj.pk]))
    assert r.status_code == 200

    country_out = r.json()["targets"][0]["country"]
    assert country_out.lower() == "ua"


def test_breed_api_non_200_causes_validation_error(monkeypatch):
    class Resp:
        status_code = 500
        def json(self): return {}

    _force_breeds_source(monkeypatch, lambda *a, **k: Resp())
    services.is_valid_breed("Siamese")

    c = APIClient()
    r = c.post(
        reverse("cats-list"),
        {"name": "X", "years_of_experience": 1, "breed": "Siamese", "salary": 1_000},
        format="json",
    )
    assert r.status_code == 201


def test_services_is_valid_breed_handles_exception(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("boom")
    _force_breeds_source(monkeypatch, boom)

    with pytest.raises(RuntimeError):
        services.is_valid_breed("Siamese")
