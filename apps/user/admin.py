from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import UserAccount, Departments, Position, AccessUrl


class UserAccountAdmin(BaseUserAdmin):
    fieldsets = ((None, {"fields": ("email", "password")}),
                 ("Personal info", {"fields": ("first_name", "last_name", "picture")},),
                 ("Company info", {"fields": ("position", "area", "signature",)},),
                 ("Important dates", {"fields": ("last_login",)}),
                 ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions",)},),
                 ("Account status", {"fields": ("is_online",)}),
                 ("Access URL", {"fields": ("access_url",)}),
                 )

    add_fieldsets = (
    (None, {"classes": ("wide",), "fields": ("email", "password1", "password2", "position", "area"), },),)

    list_display = ("email", "first_name", "last_name", "is_staff", "is_active",)
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)


admin.site.register(UserAccount, UserAccountAdmin)


@admin.register(Departments)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(AccessUrl)
class AccessUrlAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
