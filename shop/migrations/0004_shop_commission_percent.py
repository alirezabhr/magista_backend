# Generated by Django 3.2.7 on 2022-01-03 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_product_is_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='commission_percent',
            field=models.SmallIntegerField(default=5),
            preserve_default=False,
        ),
    ]
