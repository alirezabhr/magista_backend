# Generated by Django 3.2.7 on 2022-03-29 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0024_auto_20220328_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopcreationstep',
            name='step',
            field=models.CharField(choices=[('REQUESTED', 'Requested'), ('VERIFIED', 'Verified'), ('SUBMITTED', 'Submitted'), ('CREATED', 'Created')], default='REQUESTED', max_length=10),
        ),
    ]
