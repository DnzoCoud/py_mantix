# Generated by Django 5.0.4 on 2024-08-06 13:34

import django.db.models.deletion
from django.db import migrations, models


def populate_event_codes(apps, schema_editor):
    Event = apps.get_model("events", "Event")
    AutoIncrementCounter = apps.get_model("events", "AutoIncrementCounter")

    # Crear o obtener el objeto AutoIncrementCounter
    counter, created = AutoIncrementCounter.objects.get_or_create(id=1)

    # Obtener todos los eventos que no tienen un código
    events_without_code = Event.objects.filter(code="")

    # Preparar una lista de eventos a actualizar
    events_to_update = []

    for event in events_without_code:
        counter.counter += 1
        event.code = str(counter.counter).zfill(6)  # Asegurarse de que tenga 6 dígitos
        events_to_update.append(event)

    # Actualizar todos los eventos en una sola operación
    if events_to_update:
        Event.objects.bulk_update(events_to_update, ["code"])

    # Actualizar el contador con el valor actual
    counter.save()


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0016_alter_historystatus_event"),
    ]

    operations = [
        migrations.CreateModel(
            name="AutoIncrementCounter",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("counter", models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name="event",
            name="code",
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name="historystatus",
            name="event",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="history_status",
                to="events.event",
            ),
        ),
        migrations.RunPython(populate_event_codes),
        migrations.AlterField(
            model_name="event",
            name="code",
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
