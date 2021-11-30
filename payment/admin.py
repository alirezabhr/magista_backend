from django.contrib import admin

from payment.models import PaymentDetail, PaymentInvoice

# Register your models here.
admin.site.register(PaymentDetail)
admin.site.register(PaymentInvoice)
