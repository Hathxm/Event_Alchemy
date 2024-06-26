# Generated by Django 5.0.4 on 2024-06-20 05:17

import django.contrib.auth.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('managers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customusers',
            fields=[
                ('allusers_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Regular User',
                'verbose_name_plural': 'Regular Users',
            },
            bases=('managers.allusers',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
