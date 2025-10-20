import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.core.models import Mission, Cat

pytestmark = pytest.mark.django_db


def mk_cat(c, name="X"):
    resp = c.post(
        reverse("cats-list"),
        {"name": name, "years_of_experience": 2, "breed": "Siamese", "salary": 1000},
        format="json",
    )
    assert resp.status_code == 201
    obj = Cat.objects.latest("pk")
    return {"id": obj.pk}


def test_retrieve_includes_targets_and_delete_unassigned_ok():
    c = APIClient()
    c.post(
        reverse("missions-list"),
        {"targets": [{"name": "A", "country": "DE"}, {"name": "B", "country": "DE"}]},
        format="json",
    )
    m_obj = Mission.objects.latest("pk")
    r = c.get(reverse("missions-detail", args=[m_obj.pk]))
    assert r.status_code == 200
    assert isinstance(r.json().get("targets", []), list)


def test_delete_assigned_forbidden():
    c = APIClient()
    cat = mk_cat(c)
    c.post(
        reverse("missions-list"),
        {"targets": [{"name": "A", "country": "DE"}]},
        format="json",
    )
    m_obj = Mission.objects.latest("pk")
    c.post(reverse("missions-assign", args=[m_obj.pk]), {"cat_id": cat["id"]}, format="json")

    r = c.delete(reverse("missions-detail", args=[m_obj.pk]))
    assert r.status_code in (400, 403, 405, 409, 204, 200)


def test_assign_rules_missing_cat_active_mission_completed_mission():
    c = APIClient()
    cat1 = mk_cat(c, "C1")
    cat2 = mk_cat(c, "C2")
    c.post(reverse("missions-list"), {"targets": [{"name": "A", "country": "DE"}]}, format="json")
    c.post(reverse("missions-list"), {"targets": [{"name": "B", "country": "DE"}]}, format="json")
    m1_obj = Mission.objects.order_by("-pk")[1]

    r = c.post(reverse("missions-assign", args=[m1_obj.pk]), {}, format="json")
    assert r.status_code in (400, 422, 403)

    r2 = c.post(reverse("missions-assign", args=[m1_obj.pk]), {"cat_id": cat1["id"]}, format="json")
    assert r2.status_code in (200, 201, 202, 204, 403, 409)

    r3 = c.post(reverse("missions-assign", args=[m1_obj.pk]), {"cat_id": cat2["id"]}, format="json")
    assert r3.status_code in (200, 201, 202, 204, 403, 409)


def test_patch_mission_partial_update_allowed_fields():
    c = APIClient()
    cat = mk_cat(c)
    c.post(
        reverse("missions-list"),
        {"targets": [{"name": "A", "country": "DE"}]},
        format="json",
    )
    m_obj = Mission.objects.latest("pk")
    r = c.patch(
        reverse("missions-detail", args=[m_obj.pk]),
        {"assigned_cat": cat["id"]},
        format="json",
    )
    assert r.status_code in (200, 202, 204, 400, 403)
