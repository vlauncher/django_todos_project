# Generated by Django 5.2 on 2025-04-12 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='todo',
            name='archived',
            field=models.BooleanField(default=False),
        ),
    ]
