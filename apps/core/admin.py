from django.contrib import admin
from .models import Cat, Mission, Target

@admin.register(Cat)
class CatAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "years_of_experience", "breed", "salary", "created_at")
    search_fields = ("name", "breed")
    list_filter = ("breed",)

class TargetInline(admin.TabularInline):
    model = Target
    extra = 0

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ("id", "assigned_cat", "is_complete", "created_at")
    list_filter = ("is_complete",)
    inlines = [TargetInline]

@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ("id", "mission_id", "name", "country", "is_complete", "updated_at")
    search_fields = ("name",)
    list_filter = ("is_complete", "country")
