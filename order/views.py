from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404, ListAPIView

from shop.models import Product, Shop
from .models import Order, Invoice, OrderItem
from .serializers import OrderSerializer, CartSerializer, OrderItemSerializer, OrderRetrieveSerializer, \
    InvoiceSerializer, OrderItemDateTimeSerializer


# Create your views here.
class CartView(APIView):
    serializer_class = CartSerializer
    order_serializer_class = OrderSerializer
    invoice_serializer_class = InvoiceSerializer

    def post(self, request):     # create orders (just for customer)
        data = request.data
        cart_ser = self.serializer_class(data=data)
        cart_ser.is_valid(raise_exception=True)

        order_list = []

        invoice_data = {
            'customer': data['customer_id']
        }
        invoice_ser = self.invoice_serializer_class(data=invoice_data)
        invoice_ser.is_valid(raise_exception=True)
        invoice = invoice_ser.save()

        for order_sample in data['cart']:
            order_data = {
                'invoice': invoice.id,
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

        ser = self.invoice_serializer_class(invoice)
        return Response(ser.data, status=status.HTTP_201_CREATED)


class ShopOrdersView(ListAPIView):
    serializer_class = OrderRetrieveSerializer

    def get_queryset(self):
        return Order.objects.filter(shop_id=self.kwargs['shop_pk']).order_by('id')


class CustomerOrdersView(ListAPIView):
    serializer_class = OrderRetrieveSerializer

    def get_queryset(self):
        return Order.objects.filter(invoice__customer_id=self.kwargs['customer_pk']).order_by('id')


class InvoiceView(APIView):
    serializer_class = InvoiceSerializer

    def get(self, request, invoice_pk):
        invoice = get_object_or_404(Invoice, pk=invoice_pk)
        ser = self.serializer_class(invoice)
        return Response(ser.data, status=status.HTTP_200_OK)


class OrderView(APIView):
    serializer_class = OrderSerializer

    def put(self, request, order_pk):   # change status of order
        order = get_object_or_404(Order, pk=order_pk)
        try:
            new_status = request.data['status']
            payload = {
                'invoice': order.invoice.id,
                'shop': order.shop.id,
                'status': new_status,
            }
            if new_status == Order.Status.SHIPPED:
                payload['shipped_by'] = request.data['shipped_by']
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if new_status == Order.Status.VERIFIED:
            payload['verified_at'] = timezone.now()
        elif new_status == Order.Status.SHIPPED:
            payload['shipped_at'] = timezone.now()
        elif new_status == Order.Status.CANCELED:
            payload['canceled_at'] = timezone.now()

        ser = self.serializer_class(order, data=payload)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data, status=status.HTTP_200_OK)


class ShopStatsView(APIView):
    serializer_class = OrderItemDateTimeSerializer

    def get(self, request, shop_pk):
        response = {}
        get_object_or_404(Shop, pk=shop_pk)

        try:
            days = request.query_params['days']
            days = int(days)
        except KeyError:
            response["error"] = ['تعداد روز مشخص نشده است.']
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        from_date = now - timezone.timedelta(days=days+1)
        order_items = OrderItem.objects.filter(order__shop=shop_pk,
                                               order__status__range=(Order.Status.VERIFIED, Order.Status.RECEIVED),
                                               order__invoice__created_at__range=(from_date, now))
        ser = self.serializer_class(order_items, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)
