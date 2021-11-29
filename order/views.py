from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from shop.models import Product
from .models import Order, Invoice, PaymentInvoice
from .serializers import OrderSerializer, CartSerializer, OrderItemSerializer, OrderRetrieveSerializer, \
    InvoiceSerializer, PaymentInvoiceSerializer, PaymentResultSerializer, PaymentDetailSerializer

from payment.pep import Pep, PepError


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
        orders = self.query_set.filter(invoice__customer_id=customer_pk)
        ser = self.serializer_class(orders, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


class InvoiceView(APIView):
    serializer_class = InvoiceSerializer

    def get(self, request, invoice_pk):
        invoice = get_object_or_404(Invoice, pk=invoice_pk)
        ser = self.serializer_class(invoice)
        return Response(ser.data, status=status.HTTP_200_OK)


class PaymentView(APIView):
    serializer_class = PaymentInvoiceSerializer

    def post(self, request):
        """
        get ipg token and redirect url. also create Payment Invoice object
        """
        ser = InvoiceSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            invoice = Invoice.objects.get(pk=request.data.get('id'))
        except Invoice.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        amount_rial = invoice.total_amount * 10     # convert Toman to Rial
        invoice_number = str(invoice.id)
        invoice_date = str(invoice.created_at)[:19]     # format: 2021-11-29 12:58:13

        pep = Pep()
        try:
            token, redirect_url = pep.get_pep_redirect_url(amount_rial, invoice_number, invoice_date)
        except PepError as error:
            rsp = {'error': [error.error_message]}
            return Response(rsp, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        data = {
            'invoice': invoice.id,
            'amount': int(amount_rial),
            'token': token
        }
        ser = self.serializer_class(data=data)
        ser.is_valid(raise_exception=True)
        ser.save()

        response = {'url': redirect_url}
        return Response(response, status=status.HTTP_200_OK)

    def put(self, request):
        """
        check transaction status and verify payment if it was successful. also create a Payment Detail
        object and set trace number
        """
        data = request.data
        ser = PaymentResultSerializer(data=data)
        ser.is_valid(raise_exception=True)

        pep = Pep()
        try:    # check transaction status
            check_trx_response = pep.check_transaction(data['trx_reference_id'], data['invoice_number'], data['invoice_date'])
            reference_num = check_trx_response['ReferenceNumber']
            trace_num = check_trx_response['TraceNumber']
            trx_ref_id = check_trx_response['TransactionReferenceID']
            invoice_num = check_trx_response['InvoiceNumber']
            invoice_date = check_trx_response['InvoiceDate']
            amount = check_trx_response['Amount']
        except PepError as error:
            rsp = {'error': [error.error_message]}
            return Response(rsp, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:    # verify transaction
            verify_trx_response = pep.verify_payment(int(amount), str(invoice_num), invoice_date)
            masked_card_num = verify_trx_response['MaskedCardNumber']
            shaparak_ref_num = verify_trx_response['ShaparakRefNumber']
        except PepError as error:
            rsp = {'error': [error.error_message]}
            return Response(rsp, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        paid_orders = Order.objects.filter(invoice_id=invoice_num)
        for order in paid_orders:
            order.status = Order.Status.PAID
            order.save()

        payment_invoice = PaymentInvoice.objects.get(invoice=int(invoice_num))
        payment_detail = {
            'payment_invoice': payment_invoice.pk,
            'ref_number': reference_num,
            'trx_ref_id': trx_ref_id,
            'trace_number': trace_num,
            'shaparak_ref_number': shaparak_ref_num,
            'masked_card_number': masked_card_num,
        }
        ser = PaymentDetailSerializer(data=payment_detail)
        ser.is_valid(raise_exception=True)
        ser.save()

        return Response(ser.data, status=status.HTTP_202_ACCEPTED)
