from django.contrib import admin

# Register your models here.
from .models import Shop, BankCredit, TagLocation, Post, ProductImage, Product, ProductDiscount, ShopDiscount

admin.site.register(Shop)
admin.site.register(BankCredit)
admin.site.register(TagLocation)
admin.site.register(Post)
admin.site.register(ProductImage)
admin.site.register(Product)
admin.site.register(ProductDiscount)
admin.site.register(ShopDiscount)
