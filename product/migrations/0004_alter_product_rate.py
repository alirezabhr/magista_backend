# Generated by Django 3.2.7 on 2021-10-27 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_alter_product_display_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='rate',
            field=models.PositiveSmallIntegerField(null=True),
        ),
    ]
