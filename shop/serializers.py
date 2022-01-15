from rest_framework import serializers

from .models import Shop, Product, Discount, BankCredit, ProductAttribute, ProductImage, Post, TagLocation


class ShopSerializer(serializers.ModelSerializer):
    rate = serializers.ReadOnlyField()
    remaining_amount = serializers.ReadOnlyField()
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
        model = Shop
        fields = [
            'id',
            'instagram_username',
            'province',
            'city',
            'profile_pic',
            'rate',
            'created_at',
        ]


class TagLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagLocation
        fields = '__all__'


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
    tag = TagLocationSerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class ProductReadonlySerializer(serializers.ModelSerializer):
    attributes = ProductAttributeSerializer(read_only=True, many=True)
    rate = serializers.ReadOnlyField()
    tag = TagLocationSerializer(read_only=True)
    shop = serializers.SerializerMethodField('get_shop')
    display_image_url = serializers.SerializerMethodField('get_image')

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
            'tag',
            'shop',
            'display_image_url',
        ]

    def get_shop(self, product):
        return ShopPublicSerializer(product.image.post.shop).data

    def get_image(self, product):
        return product.image.display_image


class ProductImageSerializer(serializers.ModelSerializer):
    products = ProductSerializer(read_only=True, many=True)

    class Meta:
        model = ProductImage
        fields = '__all__'


class ProductImageReadonlySerializer(serializers.ModelSerializer):
    products = ProductReadonlySerializer(read_only=True, many=True)

    class Meta:
        model = ProductImage
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    has_product = serializers.ReadOnlyField()
    preview_image = serializers.ReadOnlyField()
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Post
        fields = '__all__'


class PostReadonlySerializer(serializers.ModelSerializer):
    shop = ShopPublicSerializer(read_only=True)
    has_product = serializers.ReadOnlyField()
    preview_image = serializers.ReadOnlyField()
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Post
        fields = '__all__'


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'
