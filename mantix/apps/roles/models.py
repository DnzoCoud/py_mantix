from django.db import models
# Create your models here.


class Role(models.Model):
    name = models.CharField(max_length=100, null=None, unique=True)
    is_active = models.CharField(max_length=1, default="S", null=False)
    