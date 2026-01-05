from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("skill_level", "bio")}),
    )
    list_display = ["username", "email", "skill_level", "is_staff"]
    list_filter = ["skill_level", "is_staff", "is_superuser"]
