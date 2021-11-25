from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from shop.models import Product
from .models import Invoice
from .serializers import InvoiceSerializer, CartSerializer, OrderItemSerializer, InvoiceRetrieveSerializer


# Create your views here.
class CartView(APIView):
    serializer_class = CartSerializer
    invoice_serializer_class = InvoiceSerializer

    def post(self, request):     # create invoices (just for customer)
        data = request.data
        cart_ser = self.serializer_class(data=data)
        cart_ser.is_valid(raise_exception=True)

        invoice_list = []

        for shop_order in data['cart']:
            invoice_data = {
                'shop': shop_order['shop_id'],
                'customer': data['customer_id'],
                'status': Invoice.Status.AWAITING_PAYMENT,
            }

            invoice_serializer = InvoiceSerializer(data=invoice_data)
            invoice_serializer.is_valid(raise_exception=True)
            invoice = invoice_serializer.save()

            for order in shop_order['orders']:
                try:
                    product = Product.objects.get(pk=order['product']['id'])
                except Product.DoesNotExist:
                    return Response({'error': 'product does not exist'}, status=status.HTTP_400_BAD_REQUEST)

                order_item_data = {
                    'invoice': invoice.pk,
                    'product': product.id,
                    'count': order['count'],
                    'price': product.final_price
                }

                order_item_serializer = OrderItemSerializer(data=order_item_data)
                order_item_serializer.is_valid(raise_exception=True)
                order_item_serializer.save()

            invoice_list.append(invoice)

        ser = InvoiceSerializer(invoice_list, many=True)
        return Response(ser.data, status=status.HTTP_201_CREATED)

    def put(self, request):     # pay invoices (just for customer)
        user = request.user

        data = request.data
        ser = self.invoice_serializer_class(data=data, many=True)
        ser.is_valid(raise_exception=True)

        invoice_list = []
        for invoice_data in data:
            try:
                invoice = Invoice.objects.get(pk=invoice_data['id'])
                if invoice.customer.user != user:
                    return Response(status=status.HTTP_403_FORBIDDEN)
                invoice.status = Invoice.Status.PAID
                invoice.save()
                invoice_list.append(invoice)
            except Invoice.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        ser = self.invoice_serializer_class(invoice_list, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


class ShopInvoicesView(APIView):
    serializer_class = InvoiceRetrieveSerializer
    query_set = Invoice.objects.all()

    def get(self, request, shop_pk):
        invoices = self.query_set.filter(shop_id=shop_pk)
        ser = self.serializer_class(invoices, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


class CustomerOrdersView(APIView):
    serializer_class = InvoiceRetrieveSerializer
    query_set = Invoice.objects.all()

    def get(self, request, customer_pk):
        invoices = self.query_set.filter(customer_id=customer_pk)
        ser = self.serializer_class(invoices, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)
