# Generated by Django 5.0.4 on 2024-07-22 13:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0015_remove_event_prev_status_historystatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historystatus',
            name='event',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='events.event'),
        ),
    ]
