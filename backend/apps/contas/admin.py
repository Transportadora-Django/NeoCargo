from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile, EmailChangeRequest


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Perfil"
    fields = ("role",)


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ("username", "email", "first_name", "last_name", "get_role", "is_staff", "date_joined")
    list_filter = ("is_staff", "is_superuser", "is_active", "profile__role", "date_joined")
    search_fields = ("username", "first_name", "last_name", "email")

    def get_role(self, obj):
        if hasattr(obj, "profile"):
            return obj.profile.get_role_display()
        return "-"

    get_role.short_description = "Papel"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "created_at", "updated_at")
    list_filter = ("role", "created_at")
    search_fields = ("user__username", "user__first_name", "user__last_name", "user__email")
    readonly_fields = ("created_at", "updated_at")


@admin.register(EmailChangeRequest)
class EmailChangeRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "old_email", "new_email", "created_at", "expires_at", "confirmed", "confirmed_at")
    list_filter = ("confirmed", "created_at", "expires_at")
    search_fields = ("user__username", "user__email", "old_email", "new_email")
    readonly_fields = ("token", "created_at", "confirmed_at", "expires_at")
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False  # Não permitir criar via admin

    def has_change_permission(self, request, obj=None):
        return False  # Apenas leitura


# Reregister UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
