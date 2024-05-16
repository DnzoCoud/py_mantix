from apps.events.models import Status

def seed_status():
    status_data = [
        {"name": "Programado"},
        {"name": "En ejecucion"},
        {"name": "Completado"},
        {"name": "Reprogramado"},
        {"name": "Pendiente Reprogramacion"},

        # Agrega más datos según sea necesario
    ]

    for data in status_data:
        status = Status.objects.create(**data)
        status.save()

    print("Status seeded successfully")