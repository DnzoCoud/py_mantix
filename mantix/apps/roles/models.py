from django.db import models

# Create your models here.


class Menu(models.Model):
    name = models.CharField(max_length=100, null=True, default=None)
    icon = models.CharField(max_length=100, null=True, blank=True)
    link = models.CharField(max_length=100, null=True, blank=True)
    tooltip = models.CharField(max_length=100, null=True, blank=True)
    is_menu_head = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)
    is_active = models.CharField(max_length=1, default="S", null=False)
    menus = models.ManyToManyField(Menu, through="Role_Menu", related_name="roles")
    icon = models.CharField(max_length=100, null=False, default=None)

    def __str__(self):
        return self.name


class Role_Menu(models.Model):
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        related_name="role_menus",
    )
    menu = models.ForeignKey(
        Menu,
        on_delete=models.SET_NULL,
        null=True,
        related_name="menu_roles",
    )

    class Meta:
        unique_together = ("role", "menu")

    def __str__(self):
        return f"{self.role} - {self.menu}"
