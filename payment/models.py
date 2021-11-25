from django.conf import settings
from django.utils.timezone import localtime


class IPGTokenRequestPayload:
    def __init__(self, invoice_num, invoice_date, amount, redirect_url):
        self.invoice_number = invoice_num
        self.invoice_date = invoice_date
        self.terminal_code = settings.TERMINAL_CODE
        self.merchant_code = settings.MERCHANT_CODE
        self.amount = amount
        self.redirect_address = f"https:magista.ir/payment/result/{redirect_url}"
        self.time_stamp = localtime()
        self.action = 1003
