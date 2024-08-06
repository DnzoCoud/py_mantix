from django.core.management.base import BaseCommand
from django.db import transaction
from apps.events.models import Event, AutoIncrementCounter
import math


class Command(BaseCommand):
    help = "Populates event codes with a variable length pattern based on the counter"

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            # Obtener el objeto AutoIncrementCounter
            counter, created = AutoIncrementCounter.objects.get_or_create(id=1)

            # Obtener todos los eventos que no tienen un código
            events_without_code = Event.objects.filter(code="").order_by("id")

            # Preparar una lista de eventos a actualizar
            events_to_update = []

            for i, event in enumerate(events_without_code):
                # Incrementar el contador
                counter.counter += 1

                # Calcular la longitud del código basado en el contador
                num_digits = math.ceil(math.log10(counter.counter + 1))

                # Generar el código con la longitud variable
                code_value = str(counter.counter).zfill(num_digits)
                event.code = code_value
                events_to_update.append(event)

            # Actualizar todos los eventos en una sola operación
            if events_to_update:
                Event.objects.bulk_update(events_to_update, ["code"])

            # Guardar el contador actualizado
            counter.save()

            self.stdout.write(
                self.style.SUCCESS(
                    "Successfully populated event codes with a variable length pattern."
                )
            )
