# Generated by Django 4.2.16 on 2024-11-17 20:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0020_delete_invoice"),
    ]

    operations = [
        migrations.AddField(
            model_name="pickup",
            name="status",
            field=models.CharField(
                choices=[("pending", "pending"), ("completed", "completed")],
                default="pending",
                max_length=255,
            ),
        ),
    ]