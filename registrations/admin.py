from django.contrib import admin

from .models import Participant, Team, TeamMember


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 0


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "telegram_username",
        "has_team",
        "team_name",
        "team_size",
        "role",
        "status",
        "created_at",
    )
    list_filter = ("status", "role", "has_team", "has_idea")
    search_fields = ("full_name", "phone", "telegram_username", "team_name", "team_id")
    inlines = [TeamMemberInline]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "team_id", "members_count", "created_at")
    search_fields = ("name", "team_id")


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "participant", "full_name", "telegram_username", "role")
    search_fields = ("full_name", "phone", "telegram_username")
