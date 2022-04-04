from django.contrib import admin

# Register your models here.
from .models import Category, ShopCreationStep, Shop, Shipment, OccasionallyFreeDelivery, DeliveryPrice, BankCredit, TagLocation,\
    Post, ProductImage, Product, ProductDiscount, ShopDiscount


class ShopDetailAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'rate', 'remaining_amount')


class PostDetailAdmin(admin.ModelAdmin):
    readonly_fields = ('updated_at', 'created_at')


class ProductDetailAdmin(admin.ModelAdmin):
    readonly_fields = ('updated_at', 'created_at', 'rate', 'discount_percent', 'discount_amount', 'final_price',
                       'post_shortcode')


class ShopDiscountDetailAdmin(admin.ModelAdmin):
    readonly_fields = ('start_at', 'finish_at', 'created_at')


admin.site.register(Category)
admin.site.register(ShopCreationStep)
admin.site.register(Shop, ShopDetailAdmin)
admin.site.register(Shipment)
admin.site.register(DeliveryPrice)
admin.site.register(OccasionallyFreeDelivery)
admin.site.register(BankCredit)
admin.site.register(TagLocation)
admin.site.register(Post, PostDetailAdmin)
admin.site.register(ProductImage)
admin.site.register(Product, ProductDetailAdmin)
admin.site.register(ProductDiscount)
admin.site.register(ShopDiscount, ShopDiscountDetailAdmin)
