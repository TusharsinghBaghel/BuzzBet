# Generated by Django 5.1.4 on 2025-01-11 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='points',
            field=models.PositiveIntegerField(default=1000),
        ),
    ]
