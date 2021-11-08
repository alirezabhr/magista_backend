# Generated by Django 3.2.7 on 2021-11-08 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_rename_price_product_original_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderitem',
            old_name='quantity',
            new_name='count',
        ),
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=models.IntegerField(choices=[(1, 'Awaiting Payment'), (2, 'Paid'), (3, 'Shipped'), (4, 'Received'), (5, 'Canceled')]),
        ),
    ]
