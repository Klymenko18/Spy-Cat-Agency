from django.db import models

class Cat(models.Model):
    name = models.CharField(max_length=128)
    years_of_experience = models.PositiveIntegerField()
    breed = models.CharField(max_length=128)
    salary = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Mission(models.Model):
    assigned_cat = models.ForeignKey(Cat, null=True, blank=True, on_delete=models.SET_NULL, related_name="missions")
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Target(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name="targets")
    name = models.CharField(max_length=128)
    country = models.CharField(max_length=2)
    notes = models.TextField(blank=True, default="")
    is_complete = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["mission", "name"], name="uniq_target_name_in_mission")]
