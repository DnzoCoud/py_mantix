from django.db import models
from apps.machines.models import Machine
from django.contrib.auth.models import User
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

class Event(models.Model):
    start = models.DateField(null=None)
    end = models.DateField()
    machine = models.ForeignKey(Machine, on_delete=models.DO_NOTHING, default=None)
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, default=None)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='created_events', null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='updated_events', null=True, blank=True)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='deleted_events', null=True, blank=True)

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
