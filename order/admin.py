from django.contrib import admin

# Register your models here.
from .models import IPGPayment, Order, OrderItem

admin.site.register(IPGPayment)
admin.site.register(Order)
admin.site.register(OrderItem)
