# Generated by Django 3.2.7 on 2022-01-10 04:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shop', '0001_initial'),
        ('user', '0002_customer_postal_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='user.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(0, 'Awaiting Payment'), (1, 'Paid'), (2, 'Verified'), (3, 'Shipped'), (4, 'Received'), (5, 'Canceled')])),
                ('rate', models.SmallIntegerField(null=True)),
                ('shipped_by', models.IntegerField(choices=[(0, 'Personal Delivery'), (1, 'Online Delivery'), (2, 'Offline Delivery'), (3, 'National Post')], null=True)),
                ('paid_at', models.DateTimeField(null=True)),
                ('verified_at', models.DateTimeField(null=True)),
                ('shipped_at', models.DateTimeField(null=True)),
                ('canceled_at', models.DateTimeField(null=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='order.invoice')),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shop.shop')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.PositiveIntegerField()),
                ('count', models.PositiveSmallIntegerField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='order.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shop.product')),
            ],
        ),
    ]
