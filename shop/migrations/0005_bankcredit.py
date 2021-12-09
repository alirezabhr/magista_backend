# Generated by Django 3.2.7 on 2021-12-07 13:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_shop_wallet'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankCredit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sheba', models.CharField(max_length=30)),
                ('full_name', models.CharField(max_length=60)),
                ('shop', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='shop.shop')),
            ],
        ),
    ]
