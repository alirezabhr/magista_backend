import json

from django.test import TestCase, Client
from django.urls import reverse


# Create your tests here.
class CartApiTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.cart_url = reverse('cart')

    def test_cart_payment(self):
        data = [
            {
                "product": 95,
                "count": 1
            },
            {
                "product": 85,
                "count": 3
            }
        ]
        # response = self.client.post(path=self.cart_url, data=json.dumps(data))
        # self.assertEqual(response.status_code, 200)
