from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Area(models.Model):
    name = models.CharField(null=None, unique=True, max_length=200)
    director = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='director_area', null=True, blank=True)
    deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='created_areas', null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='updated_areas', null=True, blank=True)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='deleted_areas', null=True, blank=True)

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