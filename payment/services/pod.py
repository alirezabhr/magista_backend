import json
import string
import random
from datetime import datetime
import jdatetime

import requests


class PodError(Exception):
    def __init__(self, e):
        self.error = e


class BankError(Exception):
    def __init__(self, e):
        self.error_dict = e


class Pod:
    API_URL = 'https://api.pod.ir/srv/sc/nzh/doServiceCall'
    PAYA_PRODUCT_ID = 1076566  # شناسه سرویس انتقال پایا
    __PAYA_API_KEY = 'fc5791e0a31e44d4a40cf9d49439513e'  # کلید وب‌سرویس انتقال پایا
    __BUSINESS_TOKEN = '2560c5533dc74b8ea007b33509a811a9'  # توکن کسب و کار

    def __init__(self):
        self.__username = 'service14965060'
        self.__src_deposit_num = '1409.115.14965060.1'
        self.__src_sheba = 'IR120570140911514965060001'
        self.__bank_customer_id = '14965060'

    def _gen_time_stamp(self):
        return datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f')[:-3]

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
            'body': json.dumps(data),
        }

        response = requests.post(self.API_URL, headers=headers, data=payload)
        response = json.loads(response.text)

        if response['hasError']:
            raise PodError(response)
        else:
            return response

    def withdraw(self, amount, dest_sheba, dest_full_name, description):
        # type: (int, str, str, str) -> dict

        data = {
            "Amount": amount,
            "DestinationIban": dest_sheba,
            "RecieverFullName": dest_full_name,
            "TransactionDate": self._create_transaction_date(),
            "SourceDepNum": self.__src_deposit_num,
            "Description": description,
            "TransactionId": self._create_transaction_id(),
            "IsAutoVerify": True,
            "SenderReturnDepositNumber": self.__src_deposit_num,
            "CustomerNumber": self.__bank_customer_id,
            "DestBankCode": "",
        }

        response = self._request_builder(self.PAYA_PRODUCT_ID, self.__PAYA_API_KEY, data)
        pod_ref_num = response['referenceNumber']
        result = json.loads(response['result']['result'])
        if result['IsSuccess'] and result['RsCode'] == 1:
            return_value = {'pod_ref_num': pod_ref_num, 'result': result}
            return return_value
        else:
            raise BankError(result)

    def _create_transaction_id(self):
        org_code = '4321'
        ascii_sum = 0
        random_choices = string.ascii_lowercase + string.ascii_uppercase + string.digits
        random_str = ''.join(random.choices(random_choices, k=20))
        date_time = self._gen_time_stamp()
        data = org_code + random_str + date_time

        for char in data:
            ascii_sum += ord(char)

        return f"{org_code}-{random_str}-{date_time}-{ascii_sum}"
