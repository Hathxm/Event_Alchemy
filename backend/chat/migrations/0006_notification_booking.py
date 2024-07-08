# Generated by Django 5.0.4 on 2024-07-04 19:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_notification'),
        ('user', '0008_booking_event_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='booking',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='user.booking'),
            preserve_default=False,
        ),
    ]
