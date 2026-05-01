import re

from rest_framework import serializers

from .models import Participant, Team, TeamMember


def validate_full_name(value: str) -> str:
    if len(value.strip().split()) < 2:
      raise serializers.ValidationError("ФИО должно состоять минимум из двух слов")
    return value.strip()


def validate_telegram(value: str) -> str:
    value = value.strip()
    if not re.match(r"^@[A-Za-z0-9_]{3,32}$", value):
        raise serializers.ValidationError("Telegram должен начинаться с @")
    return value


class TeamMemberSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(validators=[validate_full_name])
    telegram_username = serializers.CharField(validators=[validate_telegram])

    class Meta:
        model = TeamMember
        fields = ["id", "full_name", "phone", "telegram_username", "role", "created_at"]
        read_only_fields = ["id", "created_at"]


class RegistrationSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(validators=[validate_full_name])
    telegram_username = serializers.CharField(validators=[validate_telegram])
    team_members = TeamMemberSerializer(many=True, required=False)

    class Meta:
        model = Participant
        fields = [
            "id",
            "full_name",
            "phone",
            "telegram_username",
            "has_team",
            "team_name",
            "team_size",
            "role",
            "team_members",
            "has_idea",
            "idea_description",
            "status",
            "team_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "team_id", "created_at", "updated_at"]

    def validate(self, attrs):
        has_team = attrs.get("has_team", False)
        team_size = attrs.get("team_size", 1)
        team_members = attrs.get("team_members", [])

        if has_team:
            if not attrs.get("team_name"):
                raise serializers.ValidationError({"team_name": "Укажите название команды"})
            if team_size < 2 or team_size > 5:
                raise serializers.ValidationError({"team_size": "Команда должна быть от 2 до 5 человек"})
            if len(team_members) != team_size - 1:
                raise serializers.ValidationError({"team_members": "Заполните данные всех участников команды"})
        else:
            attrs["team_size"] = 1
            attrs["team_name"] = None
            attrs["team_members"] = []

        if not attrs.get("has_idea"):
            attrs["idea_description"] = None

        return attrs

    def create(self, validated_data):
        team_members = validated_data.pop("team_members", [])
        team_name = validated_data.get("team_name")

        if team_name:
            safe_name = re.sub(r"[^A-Za-zА-Яа-я0-9]", "", team_name).upper()[:8]
            validated_data["team_id"] = f"TEAM-{safe_name}"

        participant = Participant.objects.create(**validated_data)

        TeamMember.objects.bulk_create(
            TeamMember(participant=participant, **member)
            for member in team_members
        )

        if participant.team_name and participant.team_id:
            Team.objects.update_or_create(
                team_id=participant.team_id,
                defaults={
                    "name": participant.team_name,
                    "members_count": participant.team_size,
                },
            )

        return participant


class ParticipantSerializer(serializers.ModelSerializer):
    team_members = TeamMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Participant
        fields = [
            "id",
            "full_name",
            "phone",
            "telegram_username",
            "has_team",
            "team_name",
            "team_size",
            "role",
            "team_members",
            "has_idea",
            "idea_description",
            "status",
            "team_id",
            "created_at",
            "updated_at",
        ]


class AdminTeamMemberSerializer(serializers.ModelSerializer):
    fullName = serializers.CharField(source="full_name")
    telegramUsername = serializers.CharField(source="telegram_username")
    createdAt = serializers.DateTimeField(source="created_at")

    class Meta:
        model = TeamMember
        fields = ["id", "fullName", "phone", "telegramUsername", "role", "createdAt"]


class AdminParticipantSerializer(serializers.ModelSerializer):
    fullName = serializers.CharField(source="full_name")
    telegramUsername = serializers.CharField(source="telegram_username")
    hasTeam = serializers.BooleanField(source="has_team")
    teamName = serializers.CharField(source="team_name")
    teamSize = serializers.IntegerField(source="team_size")
    hasIdea = serializers.BooleanField(source="has_idea")
    ideaDescription = serializers.CharField(source="idea_description")
    teamId = serializers.CharField(source="team_id")
    createdAt = serializers.DateTimeField(source="created_at")
    updatedAt = serializers.DateTimeField(source="updated_at")
    teamMembers = AdminTeamMemberSerializer(source="team_members", many=True, read_only=True)

    class Meta:
        model = Participant
        fields = [
            "id",
            "fullName",
            "phone",
            "telegramUsername",
            "hasTeam",
            "teamName",
            "teamSize",
            "role",
            "hasIdea",
            "ideaDescription",
            "status",
            "teamId",
            "createdAt",
            "updatedAt",
            "teamMembers",
        ]


class ParticipantUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ["status", "team_id", "team_name"]

    def validate_status(self, value: str) -> str:
        valid = [choice[0] for choice in Participant.Status.choices]
        if value not in valid:
            raise serializers.ValidationError("Недопустимый статус")
        return value
