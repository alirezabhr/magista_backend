import json
import os

from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient


# Create your tests here.

def get_cart_post_request_data():
    file_dir = os.path.join(settings.MEDIA_ROOT, 'test')
    file_name_path = os.path.join(file_dir, 'data.json')
    file = open(file_name_path, 'r', encoding='utf-8')
    data = json.loads(file.read())
    file.close()
    return data


class CartApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        username = '09171230011'
        password = 'test_password'
        self.create_user(username, password)

    def create_user(self, phone, password):
        data = {
            'phone': phone,
            'password': password,
        }
        response = self.client.post('/user/signup/', data=data)
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='jwt ' + token)
        self.assertEqual(response.status_code, 201)

    def test_cart_create_order(self):
        data = get_cart_post_request_data()
        response = self.client.post('/order/cart/', data=data, format='json')
        print(response.data)
        print(response.status_code)
        self.assertEqual(201, 201)


