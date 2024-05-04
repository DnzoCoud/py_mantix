from django.db import models

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
    
class Machine(models.Model):
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=200)
    serial = models.CharField(max_length=100)
    last_maintenance = models.DateField()
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, default=1)
    deleted = models.BooleanField(default=False)
    def delete(self, *args, **kwargs):
        self.deleted = True
        self.save()

    def restore(self):
        self.deleted = False
        self.save()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)