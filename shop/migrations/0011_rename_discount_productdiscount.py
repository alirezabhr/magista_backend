# Generated by Django 3.2.7 on 2022-01-21 05:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0010_alter_shop_preparation'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Discount',
            new_name='ProductDiscount',
        ),
    ]
