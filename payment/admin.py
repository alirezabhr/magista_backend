from django.contrib import admin

from payment.models import PaymentDetail, PaymentInvoice, Withdraw


class PaymentDetailAdmin(admin.ModelAdmin):
    readonly_fields = ('paid_at',)


class PaymentInvoiceAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)


class WithdrawAdmin(admin.ModelAdmin):
    readonly_fields = ('paid_at',)

# Register your models here.
admin.site.register(PaymentDetail, PaymentDetailAdmin)
admin.site.register(PaymentInvoice, PaymentInvoiceAdmin)
admin.site.register(Withdraw, WithdrawAdmin)
