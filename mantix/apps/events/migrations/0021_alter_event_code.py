# Generated by Django 5.0.4 on 2024-08-06 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0020_alter_event_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="code",
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
