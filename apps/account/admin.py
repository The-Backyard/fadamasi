from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Profile, User


class ProfileInline(admin.StackedInline):
    """Inline admin interface for the Profile model."""

    model = Profile
    can_delete = False
    verbose_name_plural = _("Profile")
    fk_name = "user"
    extra = 0
    max_num = 1


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin interface for the User model."""

    list_display = (
        "username",
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
        "is_verified",
        "is_email_verified",
        "is_phone_verified",
        "date_joined",
        "last_login",
    )
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email")
    ordering = ("-date_joined",)
    filter_horizontal = ()
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser")}),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )
    inlines = (ProfileInline,)
