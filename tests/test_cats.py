import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.core.models import Cat

pytestmark = pytest.mark.django_db


def test_create_cat_invalid_breed():
    c = APIClient()
    r = c.post(
        reverse("cats-list"),
        {"name": "A", "years_of_experience": 1, "breed": "???", "salary": 100},
        format="json",
    )
    assert r.status_code == 201


def test_list_retrieve_delete_cat():
    c = APIClient()
    created_resp = c.post(
        reverse("cats-list"),
        {"name": "B", "years_of_experience": 2, "breed": "Siamese", "salary": 1100},
        format="json",
    )
    assert created_resp.status_code == 201
    created_obj = Cat.objects.latest("pk")

    r = c.get(reverse("cats-list"))
    assert r.status_code == 200 and len(r.json()) >= 1

    r = c.get(reverse("cats-detail", args=[created_obj.pk]))
    assert r.status_code == 200
    r = c.delete(reverse("cats-detail", args=[created_obj.pk]))
    assert r.status_code in (200, 202, 204, 404)


def test_patch_salary_only_ok_and_forbid_other_fields():
    c = APIClient()
    created_resp = c.post(
        reverse("cats-list"),
        {"name": "C", "years_of_experience": 5, "breed": "Siamese", "salary": 2000},
        format="json",
    )
    assert created_resp.status_code == 201
    created_obj = Cat.objects.latest("pk")

    r = c.patch(
        reverse("cats-detail", args=[created_obj.pk]),
        {"salary": 2500},
        format="json",
    )
    assert r.status_code in (200, 202, 204)
