# Generated by Django 5.1.3 on 2024-11-28 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_order_total_data_order_vendors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='tax_data',
            field=models.JSONField(blank=True, help_text="DATA Form{'taxtype':{'tax_percentage':'tax_amount'}'}", null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]