# Generated by Django 5.1.3 on 2025-07-09 19:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0004_user_user_id"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="useractivity",
            name="question",
        ),
        migrations.RemoveField(
            model_name="useractivity",
            name="user",
        ),
        migrations.DeleteModel(
            name="Question",
        ),
        migrations.DeleteModel(
            name="User",
        ),
        migrations.DeleteModel(
            name="UserActivity",
        ),
    ]
