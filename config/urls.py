from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.utils import extend_schema

# Tag "auth" for JWT endpoints
AuthTokenObtainPairView = extend_schema(tags=["auth"])(TokenObtainPairView)
AuthTokenRefreshView = extend_schema(tags=["auth"])(TokenRefreshView)
AuthTokenVerifyView = extend_schema(tags=["auth"])(TokenVerifyView)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Core app
    path("api/", include("apps.core.urls")),

    # Users CRUD
    path("api/", include("apps.users.urls")),

    # API schema and documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # JWT Auth
    path("api/auth/jwt/create/", AuthTokenObtainPairView.as_view(), name="jwt-create"),
    path("api/auth/jwt/refresh/", AuthTokenRefreshView.as_view(), name="jwt-refresh"),
    path("api/auth/jwt/verify/", AuthTokenVerifyView.as_view(), name="jwt-verify"),
]
