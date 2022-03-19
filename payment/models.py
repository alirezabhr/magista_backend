from django.db import models

from order.models import Invoice


# Create your models here.
class PaymentInvoice(models.Model):
    invoice = models.OneToOneField(Invoice, models.PROTECT)
    amount = models.IntegerField()  # amount currency is Toman
    token = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'id: {self.id} - {self.created_at}'

class PaymentDetail(models.Model):  # for IPG
    payment_invoice = models.OneToOneField(PaymentInvoice, models.PROTECT)
    ref_number = models.BigIntegerField()  # شماره ارجاع
    trx_ref_id = models.CharField(max_length=40)  # شماره ارجاع داخلی
    trace_number = models.IntegerField()  # شماره پیگیری
    shaparak_ref_number = models.CharField(max_length=40)  # شماره ارجاع شاپرک
    masked_card_number = models.CharField(max_length=20)  # شماره کارت ماسک شده
    paid_at = models.DateTimeField(auto_now_add=True)

    @property
    def amount(self):
        return self.payment_invoice.amount

    def __str__(self):
        return f'id: {self.id} - {self.paid_at}'

class Withdraw(models.Model):
    shop = models.ForeignKey('shop.Shop', models.PROTECT)
    pod_ref_num = models.CharField(max_length=20)
    # transaction_id = models.CharField(max_length=60)
    # transaction_date = models.CharField(max_length=30)
    paid_amount = models.BigIntegerField()  # amount currency is Toman (amount which is paid to online shop)
    amount_without_commission = models.BigIntegerField()  # amount currency is Toman (Commission-free amount)
    receiver_full_name = models.CharField(max_length=80)
    destination_sheba = models.CharField(max_length=30)
    # end_to_end_id = models.CharField(max_length=60)
    transaction_code = models.CharField(max_length=80)  # شماره پیگیری
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id}({self.paid_at} | amount: {self.paid_amount} | {self.destination_sheba})'
