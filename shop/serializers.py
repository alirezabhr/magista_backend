from rest_framework import serializers

from .models import Shop, Product


class ShopSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Shop
        fields = '__all__'


class ShopPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            'instagram_username',
            'province',
            'city',
            'profile_pic'
        ]
        model = Shop


class ProductSerializer(serializers.ModelSerializer):
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class ShopProductsPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'shortcode',
            'title',
            'description',
            'display_image',
            'rate',
            'original_price',
            'discount_percent',
            'final_price',
            'is_existing',
        ]
