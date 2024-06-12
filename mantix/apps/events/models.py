from django.db import models
from apps.machines.models import Machine
from apps.sign.models import User
from datetime import date
# Create your models here.

class Status(models.Model):
    name = models.CharField(max_length=100)
    deleted = models.BooleanField(default=False)
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

class Event(models.Model):
    start = models.DateField(null=None)
    end = models.DateField()
    init_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    shift = models.CharField(max_length=1, default="A")
    machine = models.ForeignKey(Machine, on_delete=models.DO_NOTHING, default=None)
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, default=None)
    # day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='events_days', default=Day.objects.get_or_create(date=date(2000, 1, 1))[0].id)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='created_events', null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='updated_events', null=True, blank=True)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='deleted_events', null=True, blank=True)
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='events_days', null=True)
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def delete(self, *args, **kwargs):
        self.deleted = True
        self.deleted_by = kwargs.pop('deleted_by', None)
        self.save()

    def restore(self, **kwargs):
        self.deleted = False
        self.deleted_by = None
        self.updated_by = kwargs.pop('updated_by', None)
        self.save()


class Activity(models.Model):
    event = models.ForeignKey(Event, related_name="activities", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)


