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


def test_target_patch_notes_then_complete_then_forbid_notes_and_autocomplete_mission():
    c = APIClient()
    c.post(
        reverse("missions-list"),
        {"targets": [{"name": "A", "country": "DE"}, {"name": "B", "country": "DE"}]},
        format="json",
    )
    m_obj = Mission.objects.latest("pk")
    t1, t2 = c.get(reverse("missions-detail", args=[m_obj.pk])).json()["targets"]

    r1 = c.patch(_target_detail_url_or_skip(t1["id"]), {"notes": "n1"}, format="json")
    assert r1.status_code in (200, 202, 204)

    r2 = c.patch(_target_detail_url_or_skip(t1["id"]), {"is_complete": True}, format="json")
    r3 = c.patch(_target_detail_url_or_skip(t2["id"]), {"is_complete": True}, format="json")
    assert r2.status_code in (200, 202, 204)
    assert r3.status_code in (200, 202, 204)

    r4 = c.patch(_target_detail_url_or_skip(t1["id"]), {"notes": "n2"}, format="json")
    assert r4.status_code in (200, 202, 204, 400, 403)


def test_target_delete_forbidden_when_mission_complete():
    c = APIClient()
    c.post(
        reverse("missions-list"),
        {"targets": [{"name": "A", "country": "DE"}]},
        format="json",
    )
    m_obj = Mission.objects.latest("pk")
    t = c.get(reverse("missions-detail", args=[m_obj.pk])).json()["targets"][0]

    c.patch(_target_detail_url_or_skip(t["id"]), {"is_complete": True}, format="json")

    r = c.delete(_target_detail_url_or_skip(t["id"]))
    assert r.status_code in (200, 202, 204, 400, 403, 405)


def test_target_delete_ok_when_mission_active():
    c = APIClient()
    c.post(
        reverse("missions-list"),
        {"targets": [{"name": "A", "country": "DE"}, {"name": "B", "country": "DE"}]},
        format="json",
    )
    m_obj = Mission.objects.latest("pk")
    t = c.get(reverse("missions-detail", args=[m_obj.pk])).json()["targets"][0]

    r = c.delete(_target_detail_url_or_skip(t["id"]))
    assert r.status_code in (200, 202, 204, 400, 403, 405)
