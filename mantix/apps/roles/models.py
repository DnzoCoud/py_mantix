from django.db import models
# Create your models here.


class Role(models.Model):
    name = models.CharField(max_length=100, null=None, unique=True)
    is_active = models.CharField(max_length=1, default="S", null=False)

# class CustomUser(AbstractUser):
#     # Relación con la tabla de roles
#     role = models.ForeignKey(Role, on_delete=models.DO_NOTHING, null=False)
#     is_director = models.BooleanField(null=True)
#     is_manager = models.BooleanField(null=True)