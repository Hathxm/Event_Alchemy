# Generated by Django 5.0.4 on 2024-07-02 13:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_chatmessage_reciever_alter_chatmessage_sender'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatroom',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_chatrooms', to=settings.AUTH_USER_MODEL),
        ),
    ]
