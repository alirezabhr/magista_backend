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
    __BUSINESS_TOKEN = '2560c5533dc74b8ea007b33509a811a9'  # توکن کسب و کار
    PAYA_PRODUCT_ID = 1076566  # شناسه سرویس انتقال پایا
    __PAYA_API_KEY = 'fc5791e0a31e44d4a40cf9d49439513e'  # کلید وب‌سرویس انتقال پایا
    DEPOSIT_TRANSACTIONS_PRODUCT_ID = 1077467  # شناسه سرویس صورتحساب سپرده
    __DEPOSIT_TRANSACTIONS_API_KEY = '570ffaf3e320456491d25bd60b09a6cd'  # کلید وب‌سرویس صورتحساب سپرده

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
            'request': json.dumps(data),
        }

        response = requests.post(self.API_URL, headers=headers, data=payload)
        response = json.loads(response.text)

        if response['hasError']:
            raise PodError(response)
        else:
            return response

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

    def deposit_transactions(self, from_date, to_date, from_time, to_time):
        # type: (str, str, str, str) -> dict

        data = {
            "DepositNumber": self.__src_deposit_num,
            "FromDate": from_date,
            "ToDate": to_date,
            "ResultCount": 15,
            "FromTime": from_time,
            "ToTime": to_time,
        }

        response = self._request_builder(self.DEPOSIT_TRANSACTIONS_PRODUCT_ID, self.__DEPOSIT_TRANSACTIONS_API_KEY, data)
        pod_ref_num = response['referenceNumber']
        result = json.loads(response['result']['result'])
        if result['IsSuccess'] and result['RsCode'] == 1:
            return_value = {'pod_ref_num': pod_ref_num, 'result': result}
            return return_value
        else:
            raise BankError(result)

    def check_transaction(self, dest_sheba):
        # type: (str) -> tuple

        delta = jdatetime.timedelta(minutes=10, days=2)
        now_date_time = jdatetime.datetime.now().date()
        from_date_time = now_date_time - delta
        to_date_time = now_date_time + delta

        from_date = from_date_time.strftime('%Y/%m/%d')
        to_date = to_date_time.strftime('%Y/%m/%d')
        from_time = from_date_time.strftime('%H:%M:%S')
        to_time = to_date_time.strftime('%H:%M:%S')

        transactions_response = self.deposit_transactions(from_date, to_date, from_time, to_time)

        trx_list = transactions_response['result']['ResultData'][0]['Statements']

        found = False
        found_trx = {}
        for trx in trx_list:
            description = trx['Description']
            start_index = description.find("IR")
            end_index = description.find(" ", start_index)
            if dest_sheba == description[start_index:end_index]:
                found_trx = trx
                found = True
                break

        return found, found_trx
