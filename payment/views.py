from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from order.models import Invoice, Order
from order.serializers import InvoiceSerializer
from payment.models import PaymentInvoice, Withdraw
from payment.serializers import PaymentInvoiceSerializer, PaymentResultSerializer, PaymentDetailSerializer, \
    WithdrawSerializer, WithdrawRequestSerializer, WithdrawPublicSerializer

from .services.pep import Pep, PepError
from .services.pod import Pod, PodError, BankError


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

        amount_rial = invoice.total_amount * 10  # convert Toman to Rial
        invoice_number = str(invoice.id)
        invoice_date = str(invoice.created_at)[:19]  # format: 2021-11-29 12:58:13

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
        try:  # check transaction status
            check_trx_response = pep.check_transaction(data['trx_reference_id'], data['invoice_number'],
                                                       data['invoice_date'])
            reference_num = check_trx_response['ReferenceNumber']
            trace_num = check_trx_response['TraceNumber']
            trx_ref_id = check_trx_response['TransactionReferenceID']
            invoice_num = check_trx_response['InvoiceNumber']
            invoice_date = check_trx_response['InvoiceDate']
            amount = check_trx_response['Amount']
        except PepError as error:
            rsp = {'error': [error.error_message]}
            return Response(rsp, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:  # verify transaction
            verify_trx_response = pep.verify_payment(int(amount), str(invoice_num), invoice_date)
            masked_card_num = verify_trx_response['MaskedCardNumber']
            shaparak_ref_num = verify_trx_response['ShaparakRefNumber']
        except PepError as error:
            rsp = {'error': [error.error_message]}
            return Response(rsp, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        paid_orders = Order.objects.filter(invoice_id=invoice_num)
        for order in paid_orders:
            order.status = Order.Status.PAID
            order.paid_at = timezone.now()
            order.save()
            # insert order total price in shop wallet
            shop = order.shop
            shop.wallet += order.total_price
            shop.save()

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


class WithdrawView(APIView):
    serializer_class = WithdrawSerializer
    request_serializer_class = WithdrawRequestSerializer
    public_serializer_class = WithdrawPublicSerializer

    def post(self, request):
        pod = Pod()
        ser = self.request_serializer_class(data=request.data)
        ser.is_valid(raise_exception=True)

        try:
            paya_response = pod.paya(request.data)
        except PodError as error:
            rsp = {'error': error.error, 'type': 'pod_error'}
            return Response(rsp, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except BankError as error:
            rsp = {'error': error.error_dict, 'type': 'bank_error'}
            return Response(rsp, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as error:
            rsp = {'error': error, 'type': 'system_error'}
            return Response(rsp, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        withdraw_data = {
            "shop": request.data['shop'],
            "pod_ref_num": paya_response['pod_ref_num'],
            "amount": request.data['amount'],
            "receiver_full_name": request.data['first_name'] + request.data['last_name'],
            "destination_sheba": request.data['sheba'],
            "transaction_code": paya_response['bank_result']['Data'],
        }
        withdraw_ser = self.serializer_class(data=withdraw_data)
        withdraw_ser.is_valid(raise_exception=True)
        withdraw_ser.save()

        withdraw = Withdraw.objects.get(transaction_code=paya_response['bank_result']['Data'])
        ser = self.public_serializer_class(withdraw)

        return Response(ser.data, status=status.HTTP_201_CREATED)

"""
THIS VIEW WORKS WITH NEW PAYA API. WHICH HAS SOME BUGS.

class WithdrawView(APIView):
    serializer_class = WithdrawSerializer
    request_serializer_class = WithdrawRequestSerializer
    public_serializer_class = WithdrawPublicSerializer

    def post(self, request):
        data = request.data

        ser = self.request_serializer_class(data=data)
        ser.is_valid(raise_exception=True)

        shop_pk = data['shop']
        amount = int(data['amount']) * 10   # Convert To Rial
        sheba = data['sheba']
        full_name = data['full_name']
        description = f'تسویه با {full_name}'

        try:
            pod = Pod()
            withdraw_response = pod.withdraw(amount, sheba, full_name, description)
        except PodError as error:
            rsp = {'error': error.error, 'type': 'pod_error'}
            return Response(rsp, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except BankError as error:
            rsp = {'error': error.error_dict, 'type': 'bank_error'}
            return Response(rsp, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as error:
            rsp = {'error': error, 'type': 'system_error'}
            return Response(rsp, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        withdraw_data = {
            "shop": shop_pk,
            "pod_ref_num": withdraw_response['pod_ref_num'],
            "transaction_id": withdraw_response['result']['TransactionId'],
            "transaction_date": withdraw_response['result']['TransactionDate'],
            "amount": withdraw_response['result']['Amount'],
            "receiver_full_name": withdraw_response['result']['RecieverFullNam'],
            "destination_sheba": withdraw_response['result']['DestinationIban'],
            "end_to_end_id": withdraw_response['result']['EndToEndId'],
            "transaction_code": withdraw_response['result']['TransactionCode'],
        }
        withdraw_ser = self.serializer_class(data=withdraw_data)
        withdraw_ser.is_valid(raise_exception=True)
        withdraw_ser.save()

        withdraw = Withdraw.objects.get(transaction_code=withdraw_response['result']['TransactionCode'])
        ser = self.public_serializer_class(withdraw)

        return Response(ser.data, status=status.HTTP_201_CREATED)

    # def _check_trx_status(self, dest_sheba):
    #     try:
    #         pod = Pod()
    #         response = pod.check_transaction(dest_sheba)
    #         if response[0]:
    #             _save_trx(response[1])
    #         else:
    #             return Response
    #     except PodError as error:
    #         rsp = {'error': error.error, 'type': 'pod_error'}
    #         return Response(rsp, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    #     except BankError as error:
    #         rsp = {'error': error.error_dict, 'type': 'bank_error'}
    #         return Response(rsp, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    #
    #     return Response(, status=status.HTTP_200_OK)
"""