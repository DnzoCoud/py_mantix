# Generated by Django 5.0.4 on 2024-08-06 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0017_autoincrementcounter_event_code_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="code",
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
