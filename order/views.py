from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404, ListAPIView

from logger.log_sentry import log_message_sentry
from shop.models import Product, Shop, ShopDiscount, DeliveryPrice
from user.models import Customer
from .models import Order, Invoice, OrderItem, OrderShopDiscount
from .serializers import OrderSerializer, CartSerializer, OrderItemSerializer, OrderRetrieveSerializer, \
    InvoiceSerializer, OrderItemDateTimeSerializer, OrderShopDiscountSerializer, OrderDeliveryPriceSerializer

from sentry_sdk import capture_exception


# Create your views here.
class CartView(APIView):
    serializer_class = CartSerializer
    order_serializer_class = OrderSerializer
    invoice_serializer_class = InvoiceSerializer
    delivery_serializer_class = OrderDeliveryPriceSerializer

    def post(self, request):     # create orders (just for customer)
        data = request.data
        cart_ser = self.serializer_class(data=data)
        if not cart_ser.is_valid():
            log_message_sentry('CartView post cart_ser', cart_ser.errors, request.data)
            return Response(cart_ser.errors, status=status.HTTP_400_BAD_REQUEST)

        order_list = []
        customer = get_object_or_404(Customer, id=data['customer_id'])

        invoice_data = {
            'customer': customer.id
        }
        invoice_ser = self.invoice_serializer_class(data=invoice_data)
        invoice_ser.is_valid(raise_exception=True)
        invoice = invoice_ser.save()

        for order_sample in data['cart']:
            delivery = get_object_or_404(DeliveryPrice, id=order_sample['delivery_id'], shipment__shop__id=order_sample['shop_id'])

            # Create Order Object
            order_data = {
                'invoice': invoice.id,
                'shop': order_sample['shop_id'],
                'status': Order.Status.AWAITING_PAYMENT,
            }

            order_serializer = self.order_serializer_class(data=order_data)
            if not order_serializer.is_valid():
                log_message_sentry('CartView post order_serializer', order_serializer.errors, request.data)
                return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            order = order_serializer.save()

            # Create Order Delivery Price Object
            delivery_data = {
                'order': order.id,
                'delivery_id': delivery.id,
                'type': delivery.type,
                'base': delivery.base,
                'per_kilo': delivery.per_kilo,
                'destination_province': customer.province,
                'destination_city': customer.city,
                'destination_address': customer.address + '\nکد پستی: ' + customer.postal_code,
            }
            delivery_serializer = self.delivery_serializer_class(data=delivery_data)
            if not delivery_serializer.is_valid():
                log_message_sentry('CartView post delivery_serializer', delivery_serializer.errors, request.data)
                return Response(delivery_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            delivery_serializer.save()

            # Create Order Item Objects
            for order_item in order_sample['order_items']:
                try:
                    product = Product.objects.get(pk=order_item['product']['id'])
                except Product.DoesNotExist as e:
                    capture_exception(error=e)
                    return Response({'error': 'product does not exist'}, status=status.HTTP_400_BAD_REQUEST)

                order_item_data = {
                    'order': order.pk,
                    'product': product.id,
                    'count': order_item['count'],
                    'product_title': product.title,
                    'product_original_price': product.original_price,
                    'product_final_price': product.final_price,
                    'product_discount_percent': product.discount_percent,
                }

                order_item_serializer = OrderItemSerializer(data=order_item_data)
                if not order_item_serializer.is_valid():
                    log_message_sentry('CartView post order_item_ser', order_item_serializer.errors, request.data)
                    return Response(order_item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                order_item_serializer.save()

            order_list.append(order)

        ser = self.invoice_serializer_class(invoice)
        return Response(ser.data, status=status.HTTP_201_CREATED)


class ShopOrdersView(ListAPIView):
    serializer_class = OrderRetrieveSerializer

    def get_queryset(self):
        return Order.objects.filter(shop_id=self.kwargs['shop_pk'], status__gt=Order.Status.AWAITING_PAYMENT).order_by('id')


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
        except KeyError as e:
            capture_exception(error=e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if new_status == Order.Status.VERIFIED:
            payload['verified_at'] = timezone.now()
        elif new_status == Order.Status.SHIPPED:
            payload['shipped_at'] = timezone.now()
        elif new_status == Order.Status.CANCELED:
            payload['canceled_at'] = timezone.now()

        ser = self.serializer_class(order, data=payload)
        if not ser.is_valid():
            log_message_sentry('OrderView post', ser.errors, request.data, level="error")
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        ser.save()
        return Response(ser.data, status=status.HTTP_200_OK)


class OrderRateView(APIView):
    serializer_class = OrderSerializer
    # TODO need a permission to check if the user is the customer in Order or not

    def post(self, request, order_pk):   # rate order
        order = get_object_or_404(Order, pk=order_pk)
        try:
            rate = request.data['rate']
        except KeyError as e:
            capture_exception(error=e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        payload = {
            'invoice': order.invoice.id,
            'shop': order.shop.id,
            'status': order.status,
            'rate': rate,
        }
        ser = self.serializer_class(order, data=payload)
        if not ser.is_valid():
            log_message_sentry('OrderRateView post', ser.errors, request.data, level="error")
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
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
        except KeyError as e:
            capture_exception(error=e)
            response["error"] = ['تعداد روز مشخص نشده است.']
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        from_date = now - timezone.timedelta(days=days+1)
        order_items = OrderItem.objects.filter(order__shop=shop_pk,
                                               order__status__range=(Order.Status.VERIFIED, Order.Status.RECEIVED),
                                               order__invoice__created_at__range=(from_date, now))
        ser = self.serializer_class(order_items, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


class ApplyShopDiscountView(APIView):

    def get_object(self, shop_pk, code):
        return ShopDiscount.objects.get(shop_id=shop_pk, code=code)     # it may raise an error if it doesn't exist

    def shop_discount_used_count(self, shop_pk, code):
        qs = OrderShopDiscount.objects.filter(shop_discount__code=code, shop_discount__shop_id=shop_pk)
        paid = [osd for osd in qs if osd.order.invoice.is_paid]
        return len(paid)

    def post(self, request, order_pk):
        try:
            code = request.data['code']
            order = get_object_or_404(Order, id=order_pk)
            order_shop_id = order.shop.id
            shop_discount = self.get_object(order_shop_id, code)
        except KeyError as e:
            capture_exception(error=e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except ShopDiscount.DoesNotExist as e:
            capture_exception(error=e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if shop_discount.is_active is False:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

        if shop_discount.count is not None:     # shop discount has count limit
            if shop_discount.count - self.shop_discount_used_count(order_shop_id, code) <= 0:
                # <= for a case when multiple customer make the invoice at the same time
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)     # discount exceeded its count limit

        if shop_discount.start_at is not None and shop_discount.end_at is not None:     # it has time limit
            now = timezone.now()
            if shop_discount.start_at > now or shop_discount.end_at < now:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)     # discount exceeded its time limit

        order_shop_discount_data = {
            'order': order.id,
            'shop_discount': shop_discount.id,
        }
        ser = OrderShopDiscountSerializer(data=order_shop_discount_data)
        ser.is_valid(raise_exception=True)
        ser.save()

        order_ser = OrderRetrieveSerializer(order)
        return Response(order_ser.data, status=status.HTTP_201_CREATED)
