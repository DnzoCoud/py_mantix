from django.db import models
from apps.events.models import Event


# Create your models here.
class WorkOrder(models.Model):
    diagnosis = models.CharField(max_length=250, default=None, null=True, blank=False)
    observation = models.CharField(max_length=250, null=True)
    cause = models.CharField(max_length=250, null=True)
    event = models.OneToOneField(
        Event, on_delete=models.CASCADE, default=None, null=True
    )
    deleted = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        self.deleted = True
        self.save()

    def restore(self, **kwargs):
        self.deleted = False
        self.save()
