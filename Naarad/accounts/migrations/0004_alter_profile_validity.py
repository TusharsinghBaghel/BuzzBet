# Generated by Django 5.1.4 on 2025-01-13 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_profile_validity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='validity',
            field=models.FloatField(default=100),
        ),
    ]
