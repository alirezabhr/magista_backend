from rest_framework import serializers

from .models import Shop, Product, Discount


class ShopSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Shop
        fields = '__all__'


class ShopPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            'id',
            'instagram_username',
            'province',
            'city',
            'profile_pic'
        ]
        model = Shop


class ProductSerializer(serializers.ModelSerializer):
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    final_price = serializers.ReadOnlyField()
    discount_percent = serializers.ReadOnlyField()
    discount_description = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = '__all__'


class ShopProductsPreviewSerializer(serializers.ModelSerializer):
    shop = ShopPreviewSerializer()

    class Meta:
        model = Product
        fields = [
            'id',
            'shortcode',
            'title',
            'description',
            'display_image',
            'rate',
            'original_price',
            'discount_percent',
            'discount_description',
            'final_price',
            'is_existing',
            'shop'
        ]
        depth = 1


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'
