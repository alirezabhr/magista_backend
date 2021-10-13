from kavenegar import *


class SMSService:
    __api_key = '2B54526A52586736396436712F584F52445045626B6A47627A4B45454B59536444394F47787974725349413D'
    __api = KavenegarAPI(__api_key)

    def __send_sms(self, phone, text):
        params = {'sender': '100047778', 'receptor': '09174347638', 'message': '.وب سرویس پیام کوتاه کاوه نگار'}
        response = self.__api.sms_send(params)
        # print(response)

    def send_otp(self, phone, otp):
        self.__send_sms(phone, otp)
