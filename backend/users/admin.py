from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from investors.models import InvestorProfile, SavedStartup
from projects.models import Project
from startups.models import StartupProfile

from .models import User



@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "role",
        "is_active",
        "is_staff",
    )
    list_filter = (
        "role",
        "is_active",
        "is_staff",
    )
    search_fields = (
        "username",
        "email",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Platform",
            {
                "fields": (
                    "role",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
        (
            "Profile",
            {
                "fields": (
                    "name",
                    "slug",
                    "about_html",
                    "short_description",
                    "contact_email",
                    "website",
                    "tags",
                    "stats",
                ),
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Platform",
            {
                "fields": (
                    "email",
                    "role",
                ),
            },
        ),
    )


admin.site.register(StartupProfile)
admin.site.register(InvestorProfile)
admin.site.register(Project)
admin.site.register(SavedStartup)
