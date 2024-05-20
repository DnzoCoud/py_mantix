from django.db import models
from apps.sign.models import User
from apps.areas.models import Area

# Create your models here.
class Location(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Asegúrate de definir el 'max_length'
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, related_name='area_locations', null=True, blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='manager_locations', null=True, blank=True)
    is_active = models.BooleanField(null=False, default=1)
    deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='created_locations', null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='updated_locations', null=True, blank=True)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='deleted_locations', null=True, blank=True)


    def delete(self, *args, **kwargs):
        self.deleted = True
        self.deleted_by = kwargs.pop('deleted_by', None)
        self.save()

    def restore(self, **kwargs):
        self.deleted = False
        self.updated_by = kwargs.pop('updated_by', None)
        self.save()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)