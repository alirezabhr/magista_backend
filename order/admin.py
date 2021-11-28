from django.contrib import admin

# Register your models here.
from .models import PaymentDetail, PaymentInvoice, Order, OrderItem

admin.site.register(PaymentDetail)
admin.site.register(PaymentInvoice)
admin.site.register(Order)
admin.site.register(OrderItem)
