from django.contrib import admin

# Register your models here.
from .models import Shop, Product, Discount

admin.site.register(Shop)
admin.site.register(Product)
admin.site.register(Discount)
