from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from investors.models import InvestorProfile, SavedStartup
from projects.models import Project
from startups.models import StartupProfile

from .models import PasswordResetAuditEvent, PasswordResetToken, User
from .password_reset import request_metadata, revoke_reset_token


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
    readonly_fields = ("created_at", "updated_at", "terms_accepted_at", "consent_ip")

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
        (
            "Consent",
            {
                "fields": (
                    "terms_accepted_at",
                    "newsletter_opt_in",
                    "consent_ip",
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


@admin.action(description="Revoke selected outstanding reset tokens")
def revoke_password_reset_tokens(modeladmin, request, queryset):
    metadata = request_metadata(request)
    revoked_count = 0
    for record in queryset:
        if revoke_reset_token(record.pk, metadata, now=timezone.now()):
            revoked_count += 1
    modeladmin.message_user(request, f"Revoked {revoked_count} reset token(s).")


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "created_at",
        "expires_at",
        "used_at",
        "revoked_at",
    )
    list_filter = ("used_at", "revoked_at")
    search_fields = ("id", "user__email")
    readonly_fields = (
        "id",
        "user",
        "token_hash",
        "created_at",
        "expires_at",
        "used_at",
        "revoked_at",
    )
    actions = (revoke_password_reset_tokens,)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PasswordResetAuditEvent)
class PasswordResetAuditEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "event_type",
        "result",
        "ip_address",
        "user_agent",
        "created_at",
    )
    list_filter = ("event_type", "result")
    search_fields = ("id", "user__email")
    readonly_fields = (
        "id",
        "user",
        "event_type",
        "result",
        "ip_address",
        "user_agent",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(StartupProfile)
admin.site.register(InvestorProfile)
admin.site.register(Project)
admin.site.register(SavedStartup)
