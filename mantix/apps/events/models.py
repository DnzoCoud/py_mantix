from django.db import models
from apps.machines.models import Machine
from apps.sign.models import User
from datetime import date


# Create your models here.
class Status(models.Model):
    name = models.CharField(max_length=100)
    deleted = models.BooleanField(default=False)
    icon = models.CharField(max_length=50, null=True, default=None)

    def delete(self, *args, **kwargs):
        self.deleted = True
        self.save()

    def restore(self):
        self.deleted = False
        self.save()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Day(models.Model):
    date = models.DateField(unique=True)
    closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def cerrar_dia(self):
        # Comprueba si todos los eventos del día están en estado '3' (cerrado)
        if self.events_days.filter(status=3).count() == self.events_days.count():
            self.closed = True
            self.save()
            return True
        return False


class AutoIncrementCounter(models.Model):
    counter = models.IntegerField(default=0)

    def __str__(self):
        return str(self.counter)


class Event(models.Model):
    start = models.DateField(null=None)
    end = models.DateField()
    init_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    shift = models.CharField(max_length=1, default="A")
    machine = models.ForeignKey(Machine, on_delete=models.DO_NOTHING, default=None)
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, default=None)
    # day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='events_days', default=Day.objects.get_or_create(date=date(2000, 1, 1))[0].id)
    code = models.CharField(max_length=10, blank=True)
    request_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="request_user",
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="created_events",
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="updated_events",
        null=True,
        blank=True,
    )
    deleted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="deleted_events",
        null=True,
        blank=True,
    )
    day = models.ForeignKey(
        Day, on_delete=models.CASCADE, related_name="events_days", null=True
    )
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super(Event, self).save(*args, **kwargs)

    def generate_code(self):
        counter, created = AutoIncrementCounter.objects.get_or_create(id=1)
        counter.counter += 1
        counter.save()
        return str(counter.counter).zfill(6)

    def delete(self, *args, **kwargs):
        self.deleted = True
        self.deleted_by = kwargs.pop("deleted_by", None)
        self.save()

    def restore(self, **kwargs):
        self.deleted = False
        self.deleted_by = None
        self.updated_by = kwargs.pop("updated_by", None)
        self.save()


# comment
class Activity(models.Model):
    event = models.ForeignKey(
        Event, related_name="activities", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    technical = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="technical_events",
        null=True,
        blank=True,
    )


class HistoryStatus(models.Model):
    event = models.OneToOneField(
        Event, on_delete=models.CASCADE, related_name="history_status"
    )
    previous_state = models.ForeignKey(
        Status,
        related_name="previous_statuses",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
    )
    actual_state = models.ForeignKey(
        Status,
        related_name="actual_statuses",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
    )
    previous_reprogram = models.BooleanField(default=False)
    prev_start = models.DateField(null=True, default=None)
    prev_end = models.DateField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class MaintenanceHistory(models.Model):
    machine = models.ForeignKey(
        Machine, on_delete=models.CASCADE, related_name="maintenance_histories"
    )
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True)
    maintenance_date = models.DateTimeField()
    performed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    event_code = models.CharField(max_length=10, blank=False, null=True, default=None)

    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.machine.name} - {self.maintenance_date} - {self.status.name if self.status else 'Maintenance'}"

    class Meta:
        verbose_name = "Maintenance History"
        verbose_name_plural = "Maintenance Histories"
