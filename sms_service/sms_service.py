import requests
import json


class SMSService:
    __api_key = "11TgeUybotjKAIzarfOEJXrXYbJcKHrhGsOD/qZ9FxU"

    def send_otp(self, phone, otp):
        url = "http://api.ghasedaksms.com/v2/send/verify"

        headers = {'apikey': self.__api_key}
        body = {
            "param1": otp,
            "receptor": phone,
            "type": 1,
            "template": "magista"
        }

        response = requests.post(url, headers=headers, data=body)

        if response.status_code != 200:
            raise Exception('bad status in sending otp message', response.status_code, response.text)

        if json.loads(response.text)['messageids'] < 1000:
            raise Exception('problem in sending otp sms', response.status_code, response.text)
