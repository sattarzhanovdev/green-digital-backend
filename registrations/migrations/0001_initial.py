from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Participant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=255)),
                ("phone", models.CharField(max_length=64)),
                ("telegram_username", models.CharField(max_length=64)),
                ("has_team", models.BooleanField(default=False)),
                ("team_name", models.CharField(blank=True, max_length=255, null=True)),
                ("team_size", models.PositiveSmallIntegerField(default=1)),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("Frontend", "Frontend"),
                            ("Backend", "Backend"),
                            ("Mobile", "Mobile"),
                            ("AI / Data Science", "AI / Data Science"),
                            ("UI/UX Design", "UI/UX Design"),
                            ("PM / Product", "PM / Product"),
                            ("Другое", "Другое"),
                        ],
                        max_length=64,
                    ),
                ),
                ("has_idea", models.BooleanField(default=False)),
                ("idea_description", models.TextField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("new", "New"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                            ("waitlist", "Waitlist"),
                        ],
                        default="new",
                        max_length=16,
                    ),
                ),
                ("team_id", models.CharField(blank=True, max_length=64, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Team",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("team_id", models.CharField(max_length=64, unique=True)),
                ("members_count", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="TeamMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=255)),
                ("phone", models.CharField(max_length=64)),
                ("telegram_username", models.CharField(max_length=64)),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("Frontend", "Frontend"),
                            ("Backend", "Backend"),
                            ("Mobile", "Mobile"),
                            ("AI / Data Science", "AI / Data Science"),
                            ("UI/UX Design", "UI/UX Design"),
                            ("PM / Product", "PM / Product"),
                            ("Другое", "Другое"),
                        ],
                        max_length=64,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "participant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="team_members",
                        to="registrations.participant",
                    ),
                ),
            ],
            options={"ordering": ["id"]},
        ),
    ]
