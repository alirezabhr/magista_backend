from django.contrib import admin

from payment.models import PaymentDetail, PaymentInvoice, Withdraw

# Register your models here.
admin.site.register(PaymentDetail)
admin.site.register(PaymentInvoice)
admin.site.register(Withdraw)
