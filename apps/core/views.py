from django.db import transaction
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404, UpdateAPIView
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Cat, Mission, Target
from .serializers import (
    CatSerializer,
    CatCreateSerializer,
    MissionSerializer,
    MissionCreateSerializer,
    TargetSerializer,
    TargetCreateSerializer,
    TargetUpdateSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=["cats"],
        description="Retrieve a list of all cats."
    ),
    retrieve=extend_schema(
        tags=["cats"],
        description="Get details of a specific cat by ID."
    ),
    create=extend_schema(
        tags=["cats"],
        description="Create a cat; breed validated via TheCatAPI."
    ),
    partial_update=extend_schema(
        tags=["cats"],
        description="Update cat salary only."
    ),
    destroy=extend_schema(
        tags=["cats"],
        description="Delete a cat by ID."
    ),
)
class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all().order_by("-id")
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.action == "create":
            return CatCreateSerializer
        if self.action in {"partial_update"}:
            return CatSerializer
        return CatSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["missions"],
        description="Retrieve all missions with related targets."
    ),
    retrieve=extend_schema(
        tags=["missions"],
        description="Get details of a specific mission by ID."
    ),
    create=extend_schema(
        tags=["missions"],
        description="Create a mission with 1–3 unique targets."
    ),
    partial_update=extend_schema(
        tags=["missions"],
        description="Partially update mission fields."
    ),
    destroy=extend_schema(
        tags=["missions"],
        description="Delete a mission unless it has an assigned cat."
    ),
)
class MissionViewSet(viewsets.ModelViewSet):
    queryset = Mission.objects.all().prefetch_related("targets").order_by("-id")
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.action == "create":
            return MissionCreateSerializer
        return MissionSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.assigned_cat_id is not None:
            return Response(
                {"detail": "Mission with assigned cat cannot be deleted"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        mission = self.get_object()
        serializer = self.get_serializer(mission, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["missions"],
        description="Assign a cat to a mission if the cat has no other active mission."
    )
    @action(detail=True, methods=["post"])
    @transaction.atomic
    def assign(self, request, pk=None):
        mission = self.get_object()
        if mission.is_complete:
            return Response(
                {"detail": "Cannot assign cat to completed mission"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cat_id = request.data.get("cat_id")
        if not cat_id:
            return Response(
                {"detail": "cat_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cat = get_object_or_404(Cat, pk=cat_id)
        if Mission.objects.filter(assigned_cat=cat, is_complete=False).exclude(pk=mission.pk).exists():
            return Response(
                {"detail": "Cat already has an active mission"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        mission.assigned_cat = cat
        mission.save(update_fields=["assigned_cat", "updated_at"])
        return Response(MissionSerializer(mission).data, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(
        tags=["targets"],
        description="List all targets."
    ),
    retrieve=extend_schema(
        tags=["targets"],
        description="Get details of a target by ID."
    ),
    create=extend_schema(
        tags=["targets"],
        description="Create a target under a mission (use POST /missions/{id}/targets/)."
    ),
    partial_update=extend_schema(
        tags=["targets"],
        description="Update target notes or completion."
    ),
    destroy=extend_schema(
        tags=["targets"],
        description="Delete a target."
    ),
)
class TargetViewSet(viewsets.ModelViewSet):
    queryset = Target.objects.select_related("mission").all().order_by("-id")
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.action in {"partial_update"}:
            return TargetUpdateSerializer
        return TargetSerializer


class TargetUpdateView(UpdateAPIView):
    serializer_class = TargetUpdateSerializer
    http_method_names = ["patch", "delete", "head", "options"]

    def get_queryset(self):
        return Target.objects.select_related("mission").all()

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["target_id"],
            mission_id=self.kwargs["mission_id"],
        )

    @extend_schema(
        tags=["targets"],
        description="Update notes or mark target as complete; forbidden if target or mission is completed."
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        tags=["targets"],
        description="Delete a target; forbidden if its mission is completed."
    )
    def delete(self, request, *args, **kwargs):
        target = self.get_object()
        if target.mission.is_complete:
            return Response(
                {"detail": "Cannot delete target from completed mission"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        target.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=["missions"],
    description="Create a single target under a specific mission."
)
class MissionTargetCreateView(viewsets.ViewSet):
    http_method_names = ["post", "head", "options"]

    def create(self, request, mission_id=None):
        mission = get_object_or_404(Mission, pk=mission_id)
        serializer = TargetCreateSerializer(
            data=request.data,
            context={"mission": mission}
        )
        serializer.is_valid(raise_exception=True)
        target = serializer.save()
        return Response(TargetSerializer(target).data, status=status.HTTP_201_CREATED)
