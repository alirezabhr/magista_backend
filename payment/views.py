from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from logger.log_sentry import log_message_sentry
from order.models import Invoice, Order
from order.serializers import InvoiceSerializer
from payment.models import PaymentInvoice, Withdraw
from payment.serializers import PaymentInvoiceSerializer, PaymentResultSerializer, PaymentDetailSerializer, \
    WithdrawSerializer, WithdrawPublicSerializer
from shop.models import Shop, BankCredit
from sms_service.sms_service import SMSService

from .services.pep import Pep, PepError
from .services.pod import Pod, PodError, BankError

from sentry_sdk import capture_exception


# Create your views here.
class PaymentView(APIView):
    serializer_class = PaymentInvoiceSerializer

    def post(self, request):
        """
        get ipg token and redirect url. also create Payment Invoice object
        """
        ser = InvoiceSerializer(data=request.data)
        if not ser.is_valid():
            log_message_sentry('PaymentView post', ser.errors, request.data, level='error')
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            invoice = Invoice.objects.get(pk=request.data.get('id'))
        except Invoice.DoesNotExist as e:
            capture_exception(error=e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        amount_rial = invoice.total_amount * 10  # convert Toman to Rial
        invoice_number = str(invoice.id)
        invoice_date = str(invoice.created_at)[:19]  # format: 2021-11-29 12:58:13

        pep = Pep()
        try:
            token, redirect_url = pep.get_pep_redirect_url(amount_rial, invoice_number, invoice_date)
        except PepError as error:
            capture_exception(error=error)
            rsp = {'error': [error.error_message]}
            return Response(rsp, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        data = {
            'invoice': invoice.id,
            'amount': int(amount_rial) // 10,  # amount changed to Toman
            'token': token
        }
        ser = self.serializer_class(data=data)
        if not ser.is_valid():
            log_message_sentry('PaymentView post', ser.errors, request.data, level='fatal')
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
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
        if not ser.is_valid():
            log_message_sentry('PaymentView put', ser.errors, request.data, level='fatal')
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

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
            capture_exception(error=error)
            rsp = {'error': [error.error_message]}
            return Response(rsp, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:  # verify transaction
            verify_trx_response = pep.verify_payment(int(amount), str(invoice_num), invoice_date)
            masked_card_num = verify_trx_response['MaskedCardNumber']
            shaparak_ref_num = verify_trx_response['ShaparakRefNumber']
        except PepError as error:
            capture_exception(error=error)
            rsp = {'error': [error.error_message]}
            return Response(rsp, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        payment_invoice = PaymentInvoice.objects.get(invoice=int(invoice_num))
        payment_detail = {
            'payment_invoice': payment_invoice.pk,
            'ref_number': reference_num,
            'trx_ref_id': trx_ref_id,
            'trace_number': trace_num,
            'shaparak_ref_number': shaparak_ref_num,
            'masked_card_number': masked_card_num,
        }
        payment_detail_ser = PaymentDetailSerializer(data=payment_detail)
        if not payment_detail_ser.is_valid():
            log_message_sentry('PaymentView put', payment_detail_ser.errors, request.data, level='fatal')
            return Response(payment_detail_ser.errors, status=status.HTTP_400_BAD_REQUEST)
        payment_detail_ser.save()

        paid_orders = Order.objects.filter(invoice_id=invoice_num)
        for order in paid_orders:
            order.status = Order.Status.PAID
            order.paid_at = timezone.now()
            order.save()
            try:
                SMSService().order_sms(order.shop.vendor.phone)
            except Exception as e:
                capture_exception(error=e)

        return Response(ser.data, status=status.HTTP_202_ACCEPTED)


class WithdrawView(APIView):
    serializer_class = WithdrawSerializer
    public_serializer_class = WithdrawPublicSerializer

    def post(self, request):
        try:
            shop_id = request.data['shop']
            sheba_num = request.data['sheba']
            shop = Shop.objects.get(pk=shop_id)
            bank_credit = BankCredit.objects.get(shop_id=shop_id, sheba=sheba_num)
        except (KeyError, Shop.DoesNotExist, BankCredit.DoesNotExist) as e:
            capture_exception(error=e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        paya_payload = {
            'amount': shop.withdrawal_amount(),
            'sheba': bank_credit.sheba,
            'first_name': bank_credit.first_name,
            'last_name': bank_credit.last_name,
        }

        if paya_payload['amount'] == 0:
            return Response(status=status.HTTP_204_NO_CONTENT)

        try:
            pod = Pod()
            paya_response = pod.paya(paya_payload)
        except PodError as error:
            capture_exception(error=error)
            rsp = {'error': error.error, 'type': 'pod_error'}
            return Response(rsp, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except BankError as error:
            capture_exception(error=error)
            rsp = {'error': error.error_dict, 'type': 'bank_error'}
            return Response(rsp, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as error:
            capture_exception(error=error)
            rsp = {'error': error, 'type': 'system_error'}
            return Response(rsp, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        withdraw_data = {
            "shop": request.data['shop'],
            "pod_ref_num": paya_response['pod_ref_num'],
            "paid_amount": shop.withdrawal_amount(),  # amount is Toman
            "amount_without_commission": shop.remaining_amount,  # amount is Toman
            "receiver_full_name": paya_payload['first_name'] + paya_payload['last_name'],
            "destination_sheba": paya_payload['sheba'],
            "transaction_code": paya_response['bank_result']['Data'],
        }
        withdraw_ser = self.serializer_class(data=withdraw_data)
        if not withdraw_ser.is_valid():
            log_message_sentry('WithdrawView post', withdraw_ser.errors, request.data, level='fatal')
            return Response(withdraw_ser.errors, status=status.HTTP_400_BAD_REQUEST)
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
