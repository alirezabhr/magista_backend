from django.contrib import admin

# Register your models here.
from .models import Invoice, OrderItem

admin.site.register(Invoice)
admin.site.register(OrderItem)
