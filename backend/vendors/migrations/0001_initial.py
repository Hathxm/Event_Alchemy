# Generated by Django 5.0.4 on 2024-06-21 10:32

import django.contrib.auth.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('managers', '0002_alter_managers_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vendors',
            fields=[
                ('allusers_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('is_vendor', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Vendor',
                'verbose_name_plural': 'Vendors',
            },
            bases=('managers.allusers',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
