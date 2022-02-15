from rest_framework import serializers

from shop.models import Product
from user.serializers import CustomerSerializer
from .models import OrderItem, Order, Invoice, OrderShopDiscount, OrderDeliveryPrice
from shop.serializers import ProductReadonlySerializer


class OrderDeliveryPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDeliveryPrice
        fields = '__all__'


class OrderItemRetrieveSerializer(serializers.ModelSerializer):
    product = ProductReadonlySerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderRetrieveSerializer(serializers.ModelSerializer):
    order_items = OrderItemRetrieveSerializer(many=True, read_only=True)
    customer = CustomerSerializer(read_only=True)
    total_original_price = serializers.ReadOnlyField()
    total_discount_amount = serializers.ReadOnlyField()
    final_price = serializers.ReadOnlyField()
    has_discount_code = serializers.ReadOnlyField()
    status_text = serializers.ReadOnlyField()
    delivery = OrderDeliveryPriceSerializer(read_only=True)
    delivery_cost = serializers.ReadOnlyField()
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        depth = 1


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderItemDateTimeSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField('get_created_at')
    # order = OrderRetrieveSerializer(read_only=True)

    def get_created_at(self, order_item):
        return order_item.order.invoice.created_at.date()

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    total_original_price = serializers.ReadOnlyField()
    total_discount_amount = serializers.ReadOnlyField()
    final_price = serializers.ReadOnlyField()
    has_discount_code = serializers.ReadOnlyField()
    status_text = serializers.ReadOnlyField()
    delivery = OrderDeliveryPriceSerializer(read_only=True)
    delivery_cost = serializers.ReadOnlyField()
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

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
    delivery_id = serializers.IntegerField()
    order_items = CartOrderItemSerializer(many=True)


class CartSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    cart = CartShopOrdersSerializer(many=True)


class InvoiceSerializer(serializers.ModelSerializer):
    orders = OrderRetrieveSerializer(many=True, read_only=True)
    total_amount = serializers.ReadOnlyField()
    is_paid = serializers.ReadOnlyField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Invoice
        fields = '__all__'


class OrderShopDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderShopDiscount
        fields = '__all__'
