from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.shortcuts import get_object_or_404

from .serializers import (
    UserPublicSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
)


class IsSelfOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user.is_staff or obj == request.user


@extend_schema_view(
    list=extend_schema(
        tags=["users"],
        summary="List users",
        description="Retrieve all users with pagination, search, and filters."
    ),
    retrieve=extend_schema(
        tags=["users"],
        summary="Get user",
        description="Get details of a specific user by ID."
    ),
    create=extend_schema(
        tags=["users"],
        summary="Create user",
        description="Create a new user account."
    ),
    partial_update=extend_schema(
        tags=["users"],
        summary="Update user",
        description="Partially update user information (PATCH only)."
    ),
    destroy=extend_schema(
        tags=["users"],
        summary="Delete user",
        description="Deactivate a user (soft delete)."
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]  
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["date_joined", "username", "email", "id"]
    ordering = ["-date_joined"]

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        if self.action in {"list", "destroy", "restore"}:
            return [permissions.IsAdminUser()]
        if self.action in {"retrieve", "partial_update", "me", "change_password"}:
            return [permissions.IsAuthenticated(), IsSelfOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action == "partial_update":
            return UserUpdateSerializer
        if self.action == "change_password":
            return ChangePasswordSerializer
        return UserPublicSerializer

    def get_queryset(self):
        queryset = self.queryset
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() in ["true", "1"])
        return queryset

    def list(self, request, *args, **kwargs):
        """Return a paginated list of all users."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserPublicSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = UserPublicSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj

    @extend_schema(
        tags=["users"],
        summary="My profile",
        description="Get the profile of the currently authenticated user."
    )
    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated], url_path="me")
    def me(self, request):
        return Response(UserPublicSerializer(request.user).data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["users"],
        summary="Change password",
        description="Change the password for the authenticated or specified user."
    )
    @action(detail=True, methods=["post"], url_path="change-password")
    def change_password(self, request, pk=None):
        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request, "user": user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["users"],
        summary="Restore user",
        description="Restore a previously deactivated user (admin only)."
    )
    @action(detail=True, methods=["post"], url_path="restore", permission_classes=[permissions.IsAdminUser])
    def restore(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        if user.is_active:
            return Response({"detail": "User already active."}, status=status.HTTP_200_OK)
        user.is_active = True
        user.save(update_fields=["is_active"])
        return Response({"detail": "User restored."}, status=status.HTTP_200_OK)
