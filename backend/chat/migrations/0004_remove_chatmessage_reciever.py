# Generated by Django 5.0.4 on 2024-07-02 13:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_alter_chatroom_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatmessage',
            name='reciever',
        ),
    ]
