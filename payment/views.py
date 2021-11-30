from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from order.models import Invoice, Order
from order.serializers import InvoiceSerializer
from payment.models import PaymentInvoice
from payment.serializers import PaymentInvoiceSerializer, PaymentResultSerializer, PaymentDetailSerializer

from .services.pep import Pep, PepError


# Create your views here.
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

