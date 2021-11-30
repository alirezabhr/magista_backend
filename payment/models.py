from django.db import models

from order.models import Invoice


# Create your models here.
class PaymentInvoice(models.Model):
    invoice = models.OneToOneField(Invoice, models.PROTECT)
    amount = models.IntegerField()
    token = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)


class PaymentDetail(models.Model):
    payment_invoice = models.OneToOneField(PaymentInvoice, models.PROTECT)
    ref_number = models.BigIntegerField()   # شماره ارجاع
    trx_ref_id = models.CharField(max_length=40)    # شماره ارجاع داخلی
    trace_number = models.IntegerField()    # شماره پیگیری
    shaparak_ref_number = models.CharField(max_length=40)   # شماره ارجاع شاپرک
    masked_card_number = models.CharField(max_length=20)    # شماره کارت ماسک شده
    paid_at = models.DateTimeField(auto_now_add=True)

    @property
    def amount(self):
        return self.payment_invoice.amount
