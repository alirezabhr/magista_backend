# Generated by Django 3.2.7 on 2022-01-21 12:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_rename_discount_productdiscount'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShopDiscount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percent', models.PositiveSmallIntegerField()),
                ('description', models.CharField(blank=True, max_length=300)),
                ('is_active', models.BooleanField(default=True)),
                ('code', models.CharField(max_length=10)),
                ('count', models.IntegerField(null=True)),
                ('start_at', models.DateTimeField(null=True)),
                ('end_at', models.DateTimeField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='shop_discount', to='shop.shop')),
            ],
        ),
    ]
