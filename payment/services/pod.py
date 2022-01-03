import requests
import json
from random import randint
from datetime import datetime
import jdatetime
from xml.dom import minidom

from Crypto.Hash import SHA1
from base64 import b64encode
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


class PodError(Exception):
    def __init__(self, e):
        self.error = e


class BankError(Exception):
    def __init__(self, e):
        self.error_dict = e


class Pod:
    API_URL = 'https://api.pod.ir/srv/sc/nzh/doServiceCall'
    __BUSINESS_TOKEN = '2560c5533dc74b8ea007b33509a811a9'  # توکن کسب و کار
    OLD_PAYA_PRODUCT_ID = 445929  # شناسه سرویس انتقال پایا
    PAYA_PRODUCT_ID = 1076566  # شناسه سرویس انتقال پایا
    __OLD_PAYA_API_KEY = '316ac5e1edf34d4b8896c167551613c8'  # کلید وب‌سرویس انتقال پایا (سرویس قدیمی)
    __PAYA_API_KEY = 'fc5791e0a31e44d4a40cf9d49439513e'  # کلید وب‌سرویس انتقال پایا
    DEPOSIT_TRANSACTIONS_PRODUCT_ID = 1077467  # شناسه سرویس صورتحساب سپرده
    __DEPOSIT_TRANSACTIONS_API_KEY = '570ffaf3e320456491d25bd60b09a6cd'  # کلید وب‌سرویس صورتحساب سپرده

    def __init__(self):
        self.__username = '14965060service'
        self.__src_deposit_num = '1409.115.14965060.1'
        self.__src_sheba = 'IR120570140911514965060001'
        self.__bank_customer_id = '14965060'

    def _gen_time_stamp(self):
        return datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f')[:-3]

    def _gen_payment_id(self):
        date_time = datetime.now().strftime('y%Ym%md%dh%Hm%Ms%S')
        random_num = str(randint(1, 1000))
        return random_num + date_time

    def _create_transaction_date(self):
        return jdatetime.datetime.now().date().strftime('%Y/%m/%d')

    def _request_builder(self, sc_product_id, sc_api_key, data):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            '_token_': self.__BUSINESS_TOKEN,
            '_token_issuer_': '1',
        }

        payload = {
            'scProductId': sc_product_id,
            'scApiKey': sc_api_key,
            'request': json.dumps(data),
            'signature': self.__make_sign(data)
        }

        response = requests.post(self.API_URL, headers=headers, data=payload)
        response = json.loads(response.text)

        if response['hasError']:
            raise PodError(response)
        else:
            return response

    def __make_sign(self, data):
        # type: (dict) -> str

        pkey = open("podkey.pem")
        pkey = pkey.read()
        rsakey = RSA.importKey(pkey)
        signer = PKCS1_v1_5.new(rsakey)
        digest = SHA1.new()
        digest.update(json.dumps(data).encode('UTF-8'))
        signature = signer.sign(digest)
        signature = b64encode(signature).decode()
        return signature

    @staticmethod
    def _process_xml_node(node_list):
        rc = []
        for node in node_list:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        string = ''.join(rc)
        return json.loads(string)

    def paya(self, data):
        # amount should be Toman
        amount = str(data['amount']) + '0'
        dest_deposit = ''
        dest_sheba = data['sheba']
        dest_first_name = data['first_name']
        dest_last_name = data['last_name']

        request = {
            "UserName": self.__username,
            "SourceDepositNumber": self.__src_deposit_num,
            "SourceSheba": self.__src_sheba,
            "DestDepositNumber": dest_deposit,
            "DestSheba": dest_sheba,
            "CentralBankTransferDetailType": "16",
            "DestFirstName": dest_first_name,
            "DestLastName": dest_last_name,
            "Amount": amount,
            "SourceComment": "",
            "DestComment": "",
            "PaymentId": self._gen_payment_id(),
            "Timestamp": self._gen_time_stamp(),
        }

        response = self._request_builder(self.OLD_PAYA_PRODUCT_ID, self.__OLD_PAYA_API_KEY, request)
        result = response["result"]
        if result["statusCode"] != 200:
            raise BankError(json.dumps(response))

        bank_result = self.convert_bank_xml_result(result["result"])
        if not bank_result['IsSuccess']:
            raise BankError(json.dumps(response))

        return {'bank_result': bank_result, 'pod_ref_num': response['referenceNumber']}

    def convert_bank_xml_result(self, xml_data):
        result_key_value = minidom.parseString(xml_data)
        return self._process_xml_node(result_key_value.getElementsByTagName('TransferMoneyResult')[0].childNodes)

    # def _create_transaction_id(self):
    #     org_code = '4321'
    #     ascii_sum = 0
    #     random_choices = string.ascii_lowercase + string.ascii_uppercase + string.digits
    #     random_str = ''.join(random.choices(random_choices, k=20))
    #     date_time = self._gen_time_stamp()
    #     data = org_code + random_str + date_time
    #
    #     for char in data:
    #         ascii_sum += ord(char)
    #
    #     return f"{org_code}-{random_str}-{date_time}-{ascii_sum}"
    #
    # def withdraw(self, amount, dest_sheba, dest_full_name, description):
    #     # type: (int, str, str, str) -> dict
    #
    #     data = {
    #         "Amount": amount,
    #         "DestinationIban": dest_sheba,
    #         "RecieverFullName": dest_full_name,
    #         "TransactionDate": self._create_transaction_date(),
    #         "SourceDepNum": self.__src_deposit_num,
    #         "Description": description,
    #         "TransactionId": self._create_transaction_id(),
    #         "IsAutoVerify": True,
    #         "SenderReturnDepositNumber": self.__src_deposit_num,
    #         "CustomerNumber": self.__bank_customer_id,
    #         "DestBankCode": "",
    #     }
    #
    #     response = self._request_builder(self.PAYA_PRODUCT_ID, self.__PAYA_API_KEY, data)
    #     pod_ref_num = response['referenceNumber']
    #     result = json.loads(response['result']['result'])
    #     if result['IsSuccess'] and result['RsCode'] == 1:
    #         return_value = {'pod_ref_num': pod_ref_num, 'result': result}
    #         return return_value
    #     else:
    #         raise BankError(result)
    #
    # def deposit_transactions(self, from_date, to_date, from_time, to_time):
    #     # type: (str, str, str, str) -> dict
    #
    #     data = {
    #         "DepositNumber": self.__src_deposit_num,
    #         "FromDate": from_date,
    #         "ToDate": to_date,
    #         "ResultCount": 15,
    #         "FromTime": from_time,
    #         "ToTime": to_time,
    #     }
    #
    #     response = self._request_builder(self.DEPOSIT_TRANSACTIONS_PRODUCT_ID, self.__DEPOSIT_TRANSACTIONS_API_KEY, data)
    #     pod_ref_num = response['referenceNumber']
    #     result = json.loads(response['result']['result'])
    #     if result['IsSuccess'] and result['RsCode'] == 1:
    #         return_value = {'pod_ref_num': pod_ref_num, 'result': result}
    #         return return_value
    #     else:
    #         raise BankError(result)
    #
    # def check_transaction(self, dest_sheba):
    #     # type: (str) -> tuple
    #
    #     delta = jdatetime.timedelta(minutes=10, days=2)
    #     now_date_time = jdatetime.datetime.now().date()
    #     from_date_time = now_date_time - delta
    #     to_date_time = now_date_time + delta
    #
    #     from_date = from_date_time.strftime('%Y/%m/%d')
    #     to_date = to_date_time.strftime('%Y/%m/%d')
    #     from_time = from_date_time.strftime('%H:%M:%S')
    #     to_time = to_date_time.strftime('%H:%M:%S')
    #
    #     transactions_response = self.deposit_transactions(from_date, to_date, from_time, to_time)
    #
    #     trx_list = transactions_response['result']['ResultData'][0]['Statements']
    #
    #     found = False
    #     found_trx = {}
    #     for trx in trx_list:
    #         description = trx['Description']
    #         start_index = description.find("IR")
    #         end_index = description.find(" ", start_index)
    #         if dest_sheba == description[start_index:end_index]:
    #             found_trx = trx
    #             found = True
    #             break
    #
    #     return found, found_trx
