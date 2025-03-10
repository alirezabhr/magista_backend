# Generated by Django 3.2.7 on 2022-01-10 04:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('order', '0001_initial'),
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Withdraw',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pod_ref_num', models.CharField(max_length=20)),
                ('paid_amount', models.BigIntegerField()),
                ('amount_without_commission', models.BigIntegerField()),
                ('receiver_full_name', models.CharField(max_length=80)),
                ('destination_sheba', models.CharField(max_length=30)),
                ('transaction_code', models.CharField(max_length=80)),
                ('paid_at', models.DateTimeField(auto_now_add=True)),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shop.shop')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('token', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('invoice', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='order.invoice')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ref_number', models.BigIntegerField()),
                ('trx_ref_id', models.CharField(max_length=40)),
                ('trace_number', models.IntegerField()),
                ('shaparak_ref_number', models.CharField(max_length=40)),
                ('masked_card_number', models.CharField(max_length=20)),
                ('paid_at', models.DateTimeField(auto_now_add=True)),
                ('payment_invoice', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='payment.paymentinvoice')),
            ],
        ),
    ]
