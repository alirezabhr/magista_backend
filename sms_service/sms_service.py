import requests
import json


class SMSService:
    __api_key = "11TgeUybotjKAIzarfOEJXrXYbJcKHrhGsOD/qZ9FxU"
    sender_number = "30005006006885"

    def __request_builder(self, url, body):
        headers = {'apikey': self.__api_key}
        response = requests.post(url, headers=headers, data=body)

        if response.status_code != 200:
            raise Exception('bad status in sending otp message', response.status_code, response.text)

        if json.loads(response.text)['messageids'] < 1000:
            raise Exception('problem in sending otp sms', response.status_code, response.text)

        return response

    def send_otp(self, phone, otp):
        url = "http://api.ghasedaksms.com/v2/send/verify"
        body = {
            "param1": otp,
            "receptor": phone,
            "type": 1,
            "template": "magista"
        }
        self.__request_builder(url, body)

    def send_simple_sms(self, message, receptor):
        url = 'http://api.ghasedaksms.com/v2/sms/send/simple'
        body = {
            "message": message,
            "sender": self.sender_number,
            "receptor": receptor,
        }
        self.__request_builder(url, body)

    def order_sms(self, receptor):
        vendor_url = 'https://vendor.magista.ir'
        message = f"بدو بیا سفارش جدید داری :)\n\nمگیستا\n{vendor_url}"
        self.send_simple_sms(message, receptor)

    def shop_request_sms(self):
        message = "درخواست فروشگاه جدید"
        self.send_simple_sms(message, "09174347638")
