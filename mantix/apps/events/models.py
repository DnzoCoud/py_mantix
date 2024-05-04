from django.db import models
from apps.machines.models import Machine
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


    deleted = models.BooleanField(default=False)
    def delete(self, *args, **kwargs):
        self.deleted = True
        self.save()

    def restore(self):
        self.deleted = False
        self.save()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
