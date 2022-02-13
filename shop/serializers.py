from rest_framework import serializers

from .models import Shop, Product, ProductDiscount, BankCredit, ProductAttribute, ProductImage, Post, TagLocation, \
    ShopDiscount, Shipment, DeliveryPrice, OccasionallyFreeDelivery


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
            'bio',
            'delivery',
            'preparation',
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
    post_shortcode = serializers.ReadOnlyField()
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
    post_shortcode = serializers.ReadOnlyField()
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
            'post_shortcode',
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


class ProductDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDiscount
        fields = '__all__'


class ShopDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopDiscount
        fields = '__all__'


class DeliveryPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryPrice
        fields = '__all__'
        read_only_fields = ('shipment',)


class OccasionallyFreeDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = OccasionallyFreeDelivery
        fields = '__all__'
        read_only_fields = ('shipment',)


class ShipmentSerializer(serializers.ModelSerializer):
    national_post = DeliveryPriceSerializer(allow_null=True)  # writable
    online_delivery = DeliveryPriceSerializer(allow_null=True)  # writable
    city_free_cost_from = OccasionallyFreeDeliverySerializer(allow_null=True)  # writable
    country_free_cost_from = OccasionallyFreeDeliverySerializer(allow_null=True)  # writable

    class Meta:
        model = Shipment
        fields = '__all__'

    def validate_national_post(self, value):
        if value is not None and value.get('type') != DeliveryPrice.DeliveryType.NATIONAL_POST:
            raise serializers.ValidationError(f'type "{value.get("type")}" is not correct')
        return value

    def validate_online_delivery(self, value):
        if value is not None and value.get('type') != DeliveryPrice.DeliveryType.ONLINE_DELIVERY:
            raise serializers.ValidationError(f'type "{value.get("type")}" is not correct')
        return value

    def validate_city_free_cost_from(self, value):
        if value is not None and value.get('type') != OccasionallyFreeDelivery.AreaType.CITY:
            raise serializers.ValidationError(f'type "{value.get("type")}" is not correct')
        return value

    def validate_country_free_cost_from(self, value):
        if value is not None and value.get('type') != OccasionallyFreeDelivery.AreaType.COUNTRY:
            raise serializers.ValidationError(f'type "{value.get("type")}" is not correct')
        return value

    def validate(self, attrs):
        if attrs['send_everywhere'] is True and attrs['country_cost'] is None:
            raise serializers.ValidationError('national cost is required')
        if attrs['send_everywhere'] is True and attrs['national_post'] is None:
            raise serializers.ValidationError('national post required when send_everywhere is True')
        if attrs['national_post'] is None and attrs['online_delivery'] is None:
            raise serializers.ValidationError('need to select at least one way for shipping')

        if attrs['city_cost'] == Shipment.FreeDelivery.OCCASIONALLY_FREE and \
                attrs['city_free_cost_from'] is None:
            raise serializers.ValidationError('set city_free_cost_from when city_cost is OCCASIONALLY_FREE')
        if attrs['country_cost'] == Shipment.FreeDelivery.OCCASIONALLY_FREE and \
                attrs['country_free_cost_from'] is None:
            raise serializers.ValidationError('set country_free_cost_from when country_cost is OCCASIONALLY_FREE')

        return attrs

    def create(self, validated_data):
        national_post_data = validated_data.pop('national_post')
        online_delivery_data = validated_data.pop('online_delivery')
        city_free_cost_from_data = validated_data.pop('city_free_cost_from')
        country_free_cost_from_data = validated_data.pop('country_free_cost_from')

        if validated_data.get('send_everywhere') is False:
            validated_data['country_cost'] = None
        shipment = Shipment.objects.create(**validated_data)

        if validated_data.get('city_cost') == Shipment.FreeDelivery.NOT_FREE or \
                validated_data.get('city_cost') == Shipment.FreeDelivery.TOTALLY_FREE:
            city_free_cost_from_data = None
        if validated_data.get('country_cost') == Shipment.FreeDelivery.NOT_FREE or \
                validated_data.get('country_cost') == Shipment.FreeDelivery.TOTALLY_FREE:
            country_free_cost_from_data = None

        if city_free_cost_from_data is not None:
            OccasionallyFreeDelivery.objects.create(shipment=shipment, **city_free_cost_from_data)
        if country_free_cost_from_data is not None:
            OccasionallyFreeDelivery.objects.create(shipment=shipment, **country_free_cost_from_data)

        if national_post_data is not None:
            DeliveryPrice.objects.create(shipment=shipment, **national_post_data)
        if online_delivery_data is not None:
            DeliveryPrice.objects.create(shipment=shipment, **online_delivery_data)
        return shipment
