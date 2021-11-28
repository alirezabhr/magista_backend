import json
import logging
from datetime import datetime

import requests
from django.conf import settings

from Crypto.Util import number
from Crypto.Hash import SHA1
from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
from base64 import b64encode, b64decode
from xml.dom import minidom


class PepError(Exception):
    def __init__(self, msg):
        self.error_message = msg


class Pep:
    URL_PAYMENT_GATEWAY = "https://pep.shaparak.ir/payment.aspx"
    URL_GET_TOKEN = "https://pep.shaparak.ir/Api/v1/Payment/GetToken"
    URL_CHECK_TRANSACTION = "https://pep.shaparak.ir/Api/v1/Payment/CheckTransactionResult"
    URL_VERIFY_PAYMENT = "https://pep.shaparak.ir/Api/v1/Payment/VerifyPayment"

    def __init__(self):
        self._terminal_id = settings.TERMINAL_CODE
        self._merchant_code = settings.MERCHANT_CODE
        self._redirect_url = "https://magista.ir/payment/result"
        self._key_pair = self._convert_xml_key_to_pem("pepkey.xml")

    def _gen_time_stamp(self):
        return datetime.now().strftime('%Y/%m/%d %H:%M:%S')

    @staticmethod
    def _process_xml_node(nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        string = ''.join(rc)
        return number.bytes_to_long(b64decode(string))

    def _convert_xml_key_to_pem(self, xml_private_key_file):
        try:
            with open(xml_private_key_file, 'rb') as pkFile:
                xml_private_key = pkFile.read()
            rsa_key_value = minidom.parseString(xml_private_key)
            modulus = self._process_xml_node(
                rsa_key_value.getElementsByTagName('Modulus')[0].childNodes)
            exponent = self._process_xml_node(
                rsa_key_value.getElementsByTagName('Exponent')[0].childNodes)
            d = self._process_xml_node(
                rsa_key_value.getElementsByTagName('D')[0].childNodes)
            p = self._process_xml_node(
                rsa_key_value.getElementsByTagName('P')[0].childNodes)
            q = self._process_xml_node(
                rsa_key_value.getElementsByTagName('Q')[0].childNodes)
            private_key = RSA.construct((modulus, exponent, d, p, q))
            return private_key
        except Exception as err:
            logging.log(logging.ERROR, 'XML file is not valid')
            raise SystemExit(err)

    # Make Sign Data ====================
    def _make_sign(self, data):
        # type: (dict) -> bytes
        key_pair = self._key_pair
        serialized_data = json.dumps(data).encode('utf8')
        hash_data = SHA1.new(serialized_data)
        signer = PKCS115_SigScheme(key_pair)
        signature = signer.sign(hash_data)
        final_sign = b64encode(signature)
        return final_sign

    def _request_builder(self, url, data):
        # type: (str, dict) -> dict

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Sign': self._make_sign(data),
        }

        payload = json.dumps(data)

        response = requests.post(url, headers=headers, data=payload)
        response = json.loads(response.text)

        if not response['IsSuccess']:
            raise PepError(response['Message'])
        else:
            return response

    def get_pep_redirect_url(self, amount, invoice_number, invoice_date, mobile='', email=''):
        # type: (str, str, str, str, str) -> tuple
        params = {
            'Amount': amount,
            'InvoiceNumber': invoice_number,
            'InvoiceDate': invoice_date,
            'Mobile': mobile,
            'Email': email,
            'Action': "1003",
            'MerchantCode': self._merchant_code,
            'TerminalCode': self._terminal_id,
            'RedirectAddress': self._redirect_url,
            'TimeStamp': self._gen_time_stamp(),
        }
        response = self._request_builder(self.URL_GET_TOKEN, params)
        return response["Token"], self.URL_PAYMENT_GATEWAY + "?n=" + response["Token"]

    def check_transaction(self, reference_id, invoice_number, invoice_date):
        # type: (str, str, str) -> dict
        params = {
            'TransactionReferenceID': reference_id,
            'InvoiceNumber': invoice_number,
            'InvoiceDate': invoice_date,
            'MerchantCode': self._merchant_code,
            'TerminalCode': self._terminal_id,
        }
        response = self._request_builder(self.URL_CHECK_TRANSACTION, params)
        return response

    def verify_payment(self, amount, invoice_number, invoice_date):
        # type: (str, str, str) -> dict
        params = {
            'amount': amount,
            'invoiceNumber': invoice_number,
            'invoiceDate': invoice_date,
            'merchantCode': self._merchant_code,
            'terminalCode': self._terminal_id,
            'timeStamp': self._gen_time_stamp(),
        }
        response = self._request_builder(self.URL_VERIFY_PAYMENT, params)
        return response
