# Generated by Django 3.2.7 on 2022-01-12 18:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_alter_shop_last_scrape'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='discount',
            name='amount',
        ),
    ]
