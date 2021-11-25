from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from shop.models import Product
from .models import Order
from .serializers import OrderSerializer, CartSerializer, OrderItemSerializer, OrderRetrieveSerializer, \
    IPGPaymentSerializer


# Create your views here.
class CartView(APIView):
    serializer_class = CartSerializer
    order_serializer_class = OrderSerializer
    payment_serializer_class = IPGPaymentSerializer

    def post(self, request):     # create orders (just for customer)
        data = request.data
        cart_ser = self.serializer_class(data=data)
        cart_ser.is_valid(raise_exception=True)

        order_list = []

        ipg_payment_data = {
            'customer': data['customer_id']
        }
        ipg_payment_ser = self.payment_serializer_class(data=ipg_payment_data)
        ipg_payment_ser.is_valid(raise_exception=True)
        ipg = ipg_payment_ser.save()

        for order_sample in data['cart']:
            order_data = {
                'ipg_payment': ipg.id,
                'shop': order_sample['shop_id'],
                'status': Order.Status.AWAITING_PAYMENT,
            }

            order_serializer = self.order_serializer_class(data=order_data)
            order_serializer.is_valid(raise_exception=True)
            order = order_serializer.save()

            for order_item in order_sample['order_items']:
                try:
                    product = Product.objects.get(pk=order_item['product']['id'])
                except Product.DoesNotExist:
                    return Response({'error': 'product does not exist'}, status=status.HTTP_400_BAD_REQUEST)

                order_item_data = {
                    'order': order.pk,
                    'product': product.id,
                    'count': order_item['count'],
                    'price': product.final_price
                }

                order_item_serializer = OrderItemSerializer(data=order_item_data)
                order_item_serializer.is_valid(raise_exception=True)
                order_item_serializer.save()

            order_list.append(order)

        ser = self.order_serializer_class(order_list, many=True)
        return Response(ser.data, status=status.HTTP_201_CREATED)

    def put(self, request):     # pay orders (just for customer)
        user = request.user

        data = request.data
        ser = self.order_serializer_class(data=data, many=True)
        ser.is_valid(raise_exception=True)

        order_list = []
        for order_data in data:
            try:
                order = Order.objects.get(pk=order_data['id'])
                if order.customer.user != user:
                    return Response(status=status.HTTP_403_FORBIDDEN)
                order.status = Order.Status.PAID
                order.save()
                order_list.append(order)
            except Order.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        ser = self.order_serializer_class(order_list, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


class ShopOrdersView(APIView):
    serializer_class = OrderRetrieveSerializer
    query_set = Order.objects.all()

    def get(self, request, shop_pk):
        orders = self.query_set.filter(shop_id=shop_pk)
        ser = self.serializer_class(orders, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


class CustomerOrdersView(APIView):
    serializer_class = OrderRetrieveSerializer
    query_set = Order.objects.all()

    def get(self, request, customer_pk):
        orders = self.query_set.filter(ipg_payment__customer_id=customer_pk)
        ser = self.serializer_class(orders, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)
