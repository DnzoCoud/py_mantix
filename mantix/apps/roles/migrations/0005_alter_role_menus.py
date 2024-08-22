# Generated by Django 5.0.4 on 2024-08-22 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roles', '0004_role_menus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='menus',
            field=models.ManyToManyField(related_name='roles', through='roles.Role_Menu', to='roles.menu'),
        ),
    ]
