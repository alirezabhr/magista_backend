from rest_framework import serializers

from shop.models import Product
from user.serializers import CustomerSerializer
from .models import OrderItem, IPGPayment, Order, Invoice
from shop.serializers import ProductSerializer


class OrderItemRetrieveSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'
        depth = 1


class OrderRetrieveSerializer(serializers.ModelSerializer):
    order_items = OrderItemRetrieveSerializer(many=True, read_only=True)
    customer = CustomerSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()
    status_text = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = '__all__'
        depth = 1


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
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
    order_items = CartOrderItemSerializer(many=True)


class CartSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    cart = CartShopOrdersSerializer(many=True)


class InvoiceSerializer(serializers.ModelSerializer):
    orders = OrderRetrieveSerializer(many=True, read_only=True)
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = Invoice
        fields = '__all__'


class IPGPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPGPayment
        fields = '__all__'
