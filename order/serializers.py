from rest_framework import serializers

from shop.models import Product
from .models import Invoice, OrderItem


class InvoiceSerializer(serializers.ModelSerializer):
    orders = serializers.ReadOnlyField()

    class Meta:
        model = Invoice
        fields = '__all__'
        depth = 1


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
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

