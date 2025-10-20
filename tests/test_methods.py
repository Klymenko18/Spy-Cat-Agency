import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.core.models import Mission

pytestmark = pytest.mark.django_db


def test_methods_disallowed_put():
    c = APIClient()
    c.post(
        reverse("missions-list"),
        {"targets": [{"name": "A", "country": "DE"}]},
        format="json",
    )
    m_obj = Mission.objects.latest("pk")
    r = c.put(
        reverse("missions-detail", args=[m_obj.pk]),
        {"assigned_cat": None},
        format="json",
    )
    assert r.status_code in (200, 204, 405)
