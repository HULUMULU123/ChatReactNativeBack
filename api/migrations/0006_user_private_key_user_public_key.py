# Generated by Django 5.1.2 on 2024-12-28 03:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_message_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='private_key',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='public_key',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
