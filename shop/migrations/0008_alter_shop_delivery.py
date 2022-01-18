# Generated by Django 3.2.7 on 2022-01-18 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_shop_delivery'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='delivery',
            field=models.IntegerField(choices=[(0, 'Not Free'), (1, 'In City'), (2, 'In Country')]),
        ),
    ]
