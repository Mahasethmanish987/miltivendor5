# Generated by Django 5.1.1 on 2024-11-19 10:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0003_alter_fooditem_created_at_alter_fooditem_updated_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fooditem',
            old_name='is_availabe',
            new_name='is_available',
        ),
    ]
