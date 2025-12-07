from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class UserAdmin(UserAdmin):
    """
    for set user admin options
    """

    model = User
    list_display = ["username", "is_staff", "is_superuser", "is_active", "is_stream"]
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "username",
        "is_stream",
    )
    readonly_fields = ["date_joined", "last_login", 'private_code', "link_of_stream"]
    search_fields = ("username",)
    ordering = [
        "username",
        "is_staff",
        "is_superuser",
        "is_active",
        "is_stream",
        "first_name",
        "last_name",
    ]

    fieldsets = (
        (
            "Authentication",
            {
                "fields": (
                    "username",
                    "password",
                    "first_name",
                    "last_name",
                    "link_of_stream",
                    "logo",
                    "description",
                    "private_code",
                )
            },
        ),
        (
            "Permissions",
            {"fields": ("is_active", "is_superuser", "is_stream")},
        ),

        ("Important Date", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            "Authentication",
            {"fields": ("username", "email" ,"password1", "password2", "first_name", "last_name")},
        ),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "is_stream")},
        ),
        ("Group&Permissions", {"fields": ("groups", "user_permissions")}),
    )