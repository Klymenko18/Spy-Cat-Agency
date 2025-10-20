from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CatViewSet, MissionViewSet, TargetUpdateView

router = DefaultRouter()
router.register(r"cats", CatViewSet, basename="cats")
router.register(r"missions", MissionViewSet, basename="missions")

urlpatterns = [
    path("", include(router.urls)),
    path("missions/<int:mission_id>/targets/<int:target_id>/", TargetUpdateView.as_view(), name="target-update"),
]
