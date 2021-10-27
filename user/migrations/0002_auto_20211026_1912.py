# Generated by Django 3.2.7 on 2021-10-26 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='address',
            field=models.TextField(default='بدون آدرس'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customer',
            name='address',
            field=models.TextField(default='بدون آدرس'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='shop',
            name='profile_pic',
            field=models.CharField(max_length=80, null=True),
        ),
    ]
