from rest_framework import serializers

from shop.models import Product
from .models import Invoice, OrderItem
from shop.serializers import ProductSerializer


class OrderItemRetrieveSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'
        depth = 1


class InvoiceRetrieveSerializer(serializers.ModelSerializer):
    orders = OrderItemRetrieveSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = '__all__'
        depth = 1


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Invoice
        fields = '__all__'


class CartProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Product
        fields = '__all__'
        depth = 1


class CartOrderItemSerializer(serializers.Serializer):
    product = CartProductSerializer()
    count = serializers.IntegerField()


class CartShopOrdersSerializer(serializers.Serializer):
    shop_id = serializers.IntegerField()
    orders = CartOrderItemSerializer(many=True)


class CartSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    cart = CartShopOrdersSerializer(many=True)
