from django.db import transaction
from rest_framework import serializers
from .models import Cat, Mission, Target



class CatSerializer(serializers.ModelSerializer):
    """Public representation of a cat."""
    class Meta:
        model = Cat
        fields = [
            "id",
            "name",
            "years_of_experience",
            "breed",
            "salary",
            "created_at",
            "updated_at",
        ]


class CatCreateSerializer(serializers.ModelSerializer):
    """Create a cat."""
    class Meta:
        model = Cat
        fields = ["name", "years_of_experience", "breed", "salary"]



class TargetSerializer(serializers.ModelSerializer):
    """Public representation of a target."""
    class Meta:
        model = Target
        fields = [
            "id",
            "name",
            "country",
            "notes",
            "is_complete",
        ]


class TargetCreateSerializer(serializers.ModelSerializer):
    """Create a new target inside a mission."""
    class Meta:
        model = Target
        fields = ["name", "country", "notes"]

    def validate(self, attrs):
        mission: Mission = self.context["mission"]
        if Target.objects.filter(mission=mission, name=attrs["name"]).exists():
            raise serializers.ValidationError(
                {"name": "Target name must be unique within this mission."}
            )
        if mission.targets.count() >= 3:
            raise serializers.ValidationError(
                {"detail": "You can assign up to 3 targets per mission."}
            )
        return attrs

    def create(self, validated_data):
        mission: Mission = self.context["mission"]
        return Target.objects.create(mission=mission, **validated_data)


class TargetUpdateSerializer(serializers.ModelSerializer):
    """Update target notes or completion status."""
    class Meta:
        model = Target
        fields = ["notes", "is_complete"]
        extra_kwargs = {
            "notes": {"required": False},
            "is_complete": {"required": False},
        }

    def validate(self, attrs):
        target: Target = self.instance
        if target.mission.is_complete:
            raise serializers.ValidationError(
                {"detail": "Cannot modify target of a completed mission."}
            )
        if target.is_complete and attrs.get("is_complete") is False:
            raise serializers.ValidationError(
                {"is_complete": "Completed target cannot be reopened."}
            )
        return attrs


class MissionTargetInlineSerializer(serializers.ModelSerializer):
    """Inline target representation used inside Mission serializer."""
    class Meta:
        model = Target
        fields = ["id", "name", "country", "notes", "is_complete"]


class MissionSerializer(serializers.ModelSerializer):
    """Public representation of a mission with targets."""
    targets = MissionTargetInlineSerializer(many=True, read_only=True)

    class Meta:
        model = Mission
        fields = [
            "id",
            "assigned_cat",
            "is_complete",
            "targets",
            "created_at",
            "updated_at",
        ]


class MissionCreateTargetItemSerializer(serializers.ModelSerializer):
    """Single target input item used when creating a mission."""
    class Meta:
        model = Target
        fields = ["name", "country", "notes"]


class MissionCreateSerializer(serializers.ModelSerializer):
    """
    Create a mission with 1..3 unique targets.
    Model Mission has only: assigned_cat (optional), is_complete, created_at, updated_at.
    """
    targets = MissionCreateTargetItemSerializer(many=True)

    class Meta:
        model = Mission
        fields = ["is_complete", "targets"]
        extra_kwargs = {"is_complete": {"required": False, "default": False}}

    def validate_targets(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError("Provide 1..3 targets.")
        if len(value) > 3:
            raise serializers.ValidationError("You can assign up to 3 targets per mission.")
        names = [t.get("name") for t in value]
        if None in names:
            raise serializers.ValidationError("Each target must include 'name'.")
        if len(names) != len(set(names)):
            raise serializers.ValidationError("Targets must have unique names within a mission.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        targets_data = validated_data.pop("targets", [])
        mission = Mission.objects.create(**validated_data)
        Target.objects.bulk_create([Target(mission=mission, **t) for t in targets_data])
        mission.refresh_from_db()
        return mission
