import csv

from django.contrib.auth import authenticate, get_user_model
from django.db.models import Count, Q
from django.http import HttpResponse
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Participant, Team
from .serializers import (
    ParticipantSerializer,
    ParticipantUpdateSerializer,
    RegistrationSerializer,
)


class RegistrationThrottle(AnonRateThrottle):
    scope = "registration"


def ensure_default_admin():
    username = __import__("os").getenv("ADMIN_USERNAME", "admin")
    password = __import__("os").getenv("ADMIN_PASSWORD", "admin12345")
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"is_staff": True, "is_superuser": True},
    )
    if created:
        user.set_password(password)
        user.save(update_fields=["password"])
    return user


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
@throttle_classes([RegistrationThrottle])
def create_registration(request):
    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"message": "Registration submitted successfully"})


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def admin_login(request):
    ensure_default_admin()
    username = request.data.get("username", "")
    password = request.data.get("password", "")
    user = authenticate(username=username, password=password)

    if not user or not user.is_staff:
        return Response({"message": "Неверный логин или пароль"}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "message": "ok",
        }
    )


class AdminRegistrationsView(generics.ListAPIView):
    serializer_class = ParticipantSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = Participant.objects.prefetch_related("team_members").all()
        search = self.request.query_params.get("search")
        role = self.request.query_params.get("role")
        status_value = self.request.query_params.get("status")
        team = self.request.query_params.get("team")

        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search)
                | Q(phone__icontains=search)
                | Q(telegram_username__icontains=search)
                | Q(team_name__icontains=search)
            )
        if role:
            queryset = queryset.filter(role=role)
        if status_value:
            queryset = queryset.filter(status=status_value)
        if team == "team":
            queryset = queryset.filter(has_team=True)
        if team == "single":
            queryset = queryset.filter(has_team=False)

        return queryset


class AdminRegistrationDetailView(generics.RetrieveUpdateAPIView):
    queryset = Participant.objects.prefetch_related("team_members").all()
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return ParticipantUpdateSerializer
        return ParticipantSerializer

    def perform_update(self, serializer):
        participant = serializer.save()
        if participant.team_name and participant.team_id:
            Team.objects.update_or_create(
                team_id=participant.team_id,
                defaults={
                    "name": participant.team_name,
                    "members_count": Participant.objects.filter(team_id=participant.team_id).count(),
                },
            )


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def dashboard(request):
    total = Participant.objects.count()
    teams = Team.objects.count()
    singles = Participant.objects.filter(has_team=False).count()
    team_members_total = sum(item.team_members.count() for item in Participant.objects.prefetch_related("team_members"))
    total_people = total + team_members_total

    by_role = {role: 0 for role, _ in Participant.ROLE_CHOICES}
    for row in Participant.objects.values("role").annotate(count=Count("id")):
        by_role[row["role"]] = by_role.get(row["role"], 0) + row["count"]
    for participant in Participant.objects.prefetch_related("team_members"):
        for member in participant.team_members.all():
            by_role[member.role] = by_role.get(member.role, 0) + 1

    by_status = {status_value: 0 for status_value, _ in Participant.Status.choices}
    for row in Participant.objects.values("status").annotate(count=Count("id")):
        by_status[row["status"]] = row["count"]

    return Response(
        {
            "total": total,
            "totalPeople": total_people,
            "teams": teams,
            "singles": singles,
            "byRole": by_role,
            "byStatus": by_status,
        }
    )


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def export_csv(request):
    export_type = request.query_params.get("type")
    queryset = Participant.objects.prefetch_related("team_members").all()

    if export_type == "single":
        queryset = queryset.filter(has_team=False)
    elif export_type == "team":
        queryset = queryset.filter(has_team=True)
    elif export_type == "approved":
        queryset = queryset.filter(status=Participant.Status.APPROVED)

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="green-digital-{export_type or "all"}.csv"'
    response.write("\ufeff")
    writer = csv.writer(response)
    writer.writerow(
        [
            "ID",
            "ФИО",
            "Телефон",
            "Telegram",
            "Есть команда",
            "Название команды",
            "Количество человек",
            "Роль",
            "Есть идея",
            "Идея",
            "Состав команды",
            "Статус",
            "TeamID",
            "Дата регистрации",
        ]
    )

    for row in queryset:
        members = "; ".join(
            f"{member.full_name} / {member.phone} / {member.telegram_username} / {member.role}"
            for member in row.team_members.all()
        )
        writer.writerow(
            [
                row.id,
                row.full_name,
                row.phone,
                row.telegram_username,
                "Да" if row.has_team else "Нет",
                row.team_name or "",
                row.team_size,
                row.role,
                "Да" if row.has_idea else "Нет",
                row.idea_description or "",
                members,
                row.status,
                row.team_id or "",
                row.created_at.isoformat(),
            ]
        )

    return response
