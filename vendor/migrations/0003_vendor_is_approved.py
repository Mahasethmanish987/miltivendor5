# Generated by Django 5.1.1 on 2024-11-18 03:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0002_vendor_vendor_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]
