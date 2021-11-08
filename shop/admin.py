from django.contrib import admin

# Register your models here.
from .models import Shop, Product, Discount, Invoice, OrderItem

admin.site.register(Shop)
admin.site.register(Product)
admin.site.register(Discount)
admin.site.register(Invoice)
admin.site.register(OrderItem)
