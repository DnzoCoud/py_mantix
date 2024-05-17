from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.roles.models import Role
# Create your models here.
class User(AbstractUser):
    is_director = models.BooleanField(null=True)
    is_manager = models.BooleanField(null=True)
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING)