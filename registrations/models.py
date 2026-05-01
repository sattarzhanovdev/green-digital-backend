from django.db import models


class Participant(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        WAITLIST = "waitlist", "Waitlist"

    ROLE_CHOICES = [
        ("Frontend", "Frontend"),
        ("Backend", "Backend"),
        ("Mobile", "Mobile"),
        ("AI / Data Science", "AI / Data Science"),
        ("UI/UX Design", "UI/UX Design"),
        ("PM / Product", "PM / Product"),
        ("Другое", "Другое"),
    ]

    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=64)
    telegram_username = models.CharField(max_length=64)
    has_team = models.BooleanField(default=False)
    team_name = models.CharField(max_length=255, blank=True, null=True)
    team_size = models.PositiveSmallIntegerField(default=1)
    role = models.CharField(max_length=64, choices=ROLE_CHOICES)
    has_idea = models.BooleanField(default=False)
    idea_description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.NEW)
    team_id = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.full_name


class Team(models.Model):
    name = models.CharField(max_length=255)
    team_id = models.CharField(max_length=64, unique=True)
    members_count = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class TeamMember(models.Model):
    participant = models.ForeignKey(
        Participant,
        related_name="team_members",
        on_delete=models.CASCADE,
    )
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=64)
    telegram_username = models.CharField(max_length=64)
    role = models.CharField(max_length=64, choices=Participant.ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return self.full_name
