# Generated by Django 5.0.4 on 2024-06-28 10:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_booking_services'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='user.customusers'),
        ),
    ]
