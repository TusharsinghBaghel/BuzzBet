# Generated by Django 5.1.4 on 2025-01-11 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='newspost',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='news/'),
        ),
    ]
