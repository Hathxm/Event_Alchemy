# Generated by Django 5.0.4 on 2024-06-25 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('superadmin', '0005_events_description_events_image'),
        ('user', '0003_booking'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='services',
            field=models.ManyToManyField(blank=True, to='superadmin.services'),
        ),
    ]
