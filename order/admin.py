from django.contrib import admin

# Register your models here.
from .models import Invoice, Order, OrderItem

admin.site.register(Invoice)
admin.site.register(Order)
admin.site.register(OrderItem)
