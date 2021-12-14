from rest_framework import serializers

from .models import Shop, Product, Discount, BankCredit, ProductAttribute, ProductImage, Post


class ShopSerializer(serializers.ModelSerializer):
    rate = serializers.ReadOnlyField()
    withdrawal_amount = serializers.ReadOnlyField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Shop
        fields = '__all__'


class BankCreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankCredit
        fields = '__all__'


class ShopPublicSerializer(serializers.ModelSerializer):
    rate = serializers.ReadOnlyField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        fields = [
            'id',
            'instagram_username',
            'province',
            'city',
            'profile_pic',
            'rate',
            'created_at',
        ]
        model = Shop


class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    attributes = ProductAttributeSerializer(read_only=True, many=True)
    rate = serializers.ReadOnlyField()
    final_price = serializers.ReadOnlyField()
    discount_percent = serializers.ReadOnlyField()
    discount_description = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = '__all__'


class ProductPublicSerializer(serializers.ModelSerializer):
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    attributes = ProductAttributeSerializer(read_only=True, many=True)
    rate = serializers.ReadOnlyField()
    final_price = serializers.ReadOnlyField()
    discount_percent = serializers.ReadOnlyField()
    discount_description = serializers.ReadOnlyField()
    shop = ShopPublicSerializer()

    class Meta:
        model = Product
        fields = '__all__'


class ShopProductsPreviewSerializer(serializers.ModelSerializer):
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    attributes = ProductAttributeSerializer(read_only=True, many=True)
    rate = serializers.ReadOnlyField()
    shop = ShopPublicSerializer()

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'description',
            'image',
            'rate',
            'original_price',
            'discount_percent',
            'attributes',
            'discount_description',
            'final_price',
            'is_existing',
            'updated_at',
            'created_at',
            'shop'
        ]
        depth = 1


class ProductImageSerializer(serializers.ModelSerializer):
    products = ProductPublicSerializer(read_only=True, many=True)

    class Meta:
        model = ProductImage
        fields = '__all__'


class ProductImageReadonlySerializer(serializers.ModelSerializer):
    products = ProductPublicSerializer(read_only=True, many=True)

    class Meta:
        model = ProductImage
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    product_images = ProductImageReadonlySerializer(read_only=True, many=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Post
        fields = '__all__'


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'
