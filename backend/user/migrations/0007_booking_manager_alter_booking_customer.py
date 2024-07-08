# Generated by Django 5.0.4 on 2024-06-28 11:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('managers', '0004_venues_image4'),
        ('user', '0006_alter_booking_services'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='manager',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='managers.managers'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='booking',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.customusers'),
        ),
    ]