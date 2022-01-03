# Generated by Django 3.2.7 on 2022-01-03 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_shop_commission_percent'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bankcredit',
            old_name='full_name',
            new_name='first_name',
        ),
        migrations.AddField(
            model_name='bankcredit',
            name='last_name',
            field=models.CharField(default='بحرالعلوم', max_length=60),
            preserve_default=False,
        ),
    ]
