import random
import string

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from shop.models import DeliveryPrice, Shipment, OccasionallyFreeDelivery


# Create your tests here.
class CartApiTest(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
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


class ShopShipmentTests(APITestCase):
    __correct_data_set = [
            {
                "shop": 1,
                "send_everywhere": True,
                "has_national_post": True,
                "has_online_delivery": False,
                "national_post": {
                    "type": DeliveryPrice.DeliveryType.NATIONAL_POST,
                    "base": 15000,
                    "per_kilo": 2700
                },
                "online_delivery": None,
                "city_cost": Shipment.FreeDelivery.NOT_FREE,
                "country_cost": Shipment.FreeDelivery.OCCASIONALLY_FREE,
                "city_free_cost_from": None,
                "country_free_cost_from": {
                    "type": OccasionallyFreeDelivery.AreaType.COUNTRY,
                    "free_from": 180000
                }
            },
            {
                "shop": 2,
                "send_everywhere": True,
                "has_national_post": True,
                "has_online_delivery": True,
                "national_post": {
                    "type": DeliveryPrice.DeliveryType.NATIONAL_POST,
                    "base": 15000,
                    "per_kilo": 2700
                },
                "online_delivery": {
                    "type": DeliveryPrice.DeliveryType.ONLINE_DELIVERY,
                    "base": 13000,
                    "per_kilo": 2300
                },
                "city_cost": Shipment.FreeDelivery.TOTALLY_FREE,
                "country_cost": Shipment.FreeDelivery.NOT_FREE,
                "city_free_cost_from": None,
                "country_free_cost_from": None
            },
            {
                "shop": 3,
                "send_everywhere": False,
                "has_national_post": False,
                "has_online_delivery": True,
                "national_post": None,
                "online_delivery": {
                    "type": DeliveryPrice.DeliveryType.ONLINE_DELIVERY,
                    "base": 13000,
                    "per_kilo": 2300
                },
                "city_cost": Shipment.FreeDelivery.TOTALLY_FREE,
                "country_cost": Shipment.FreeDelivery.NOT_FREE,
                "city_free_cost_from": {
                    "type": OccasionallyFreeDelivery.AreaType.CITY,
                    "free_from": 140000
                },  # this field should be None in response
                "country_free_cost_from": None
            },
            {
                "shop": 4,
                "send_everywhere": False,
                "has_national_post": True,
                "has_online_delivery": False,
                "national_post": {
                    'type': DeliveryPrice.DeliveryType.NATIONAL_POST,
                    'base': 26000,
                    'per_kilo': 3200,
                },
                "online_delivery": None,
                "city_cost": Shipment.FreeDelivery.NOT_FREE,
                "country_cost": Shipment.FreeDelivery.NOT_FREE,
                "city_free_cost_from": None,
                "country_free_cost_from": None
            },
            {
                "shop": 5,
                "send_everywhere": False,
                "has_national_post": True,
                "has_online_delivery": False,
                "national_post": {
                    'type': DeliveryPrice.DeliveryType.NATIONAL_POST,
                    'base': 13000,
                    'per_kilo': 2700,
                },
                "online_delivery": None,
                "city_cost": Shipment.FreeDelivery.NOT_FREE,
                "country_cost": None,
                "city_free_cost_from": None,
                "country_free_cost_from": None
            },
            {
                "shop": 6,
                "send_everywhere": False,
                "has_national_post": False,
                "has_online_delivery": True,
                "national_post": None,
                "online_delivery": {
                    'type': DeliveryPrice.DeliveryType.ONLINE_DELIVERY,
                    'base': 15000,
                    'per_kilo': 2000,
                },
                "city_cost": Shipment.FreeDelivery.OCCASIONALLY_FREE,
                "country_cost": None,
                "city_free_cost_from": {
                    "type": OccasionallyFreeDelivery.AreaType.CITY,
                    "free_from": 140000
                },
                "country_free_cost_from": None
            },
            {
                "shop": 7,
                "send_everywhere": True,
                "has_national_post": True,
                "has_online_delivery": False,
                "national_post": {
                    'type': DeliveryPrice.DeliveryType.NATIONAL_POST,
                    'base': 13000,
                    'per_kilo': 2700,
                },
                "online_delivery": None,
                "city_cost": Shipment.FreeDelivery.OCCASIONALLY_FREE,
                "country_cost": Shipment.FreeDelivery.NOT_FREE,
                "city_free_cost_from": {
                    "type": OccasionallyFreeDelivery.AreaType.CITY,
                    "free_from": 120000
                },
                "country_free_cost_from": None
            },
            {
                "shop": 8,
                "send_everywhere": True,
                "has_national_post": True,
                "has_online_delivery": True,
                "national_post": {
                    'type': DeliveryPrice.DeliveryType.NATIONAL_POST,
                    'base': 13000,
                    'per_kilo': 2700,
                },
                "online_delivery": {
                    'type': DeliveryPrice.DeliveryType.ONLINE_DELIVERY,
                    'base': 17000,
                    'per_kilo': 4600,
                },
                "city_cost": Shipment.FreeDelivery.OCCASIONALLY_FREE,
                "country_cost": Shipment.FreeDelivery.NOT_FREE,
                "city_free_cost_from": {
                    "type": OccasionallyFreeDelivery.AreaType.CITY,
                    "free_from": 120000
                },
                "country_free_cost_from": None
            },
        ]

    def setUp(self) -> None:
        self.client = APIClient()
        self.vendor = self.create_vendor()
        self.client.credentials(HTTP_AUTHORIZATION=f'jwt {self.vendor.get("token")}')

    def create_vendor(self):
        url = reverse('signup')
        data = {'phone': '09123456789', 'password': 'magista_magista'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data

    def create_shop(self, instagram_username, instagram_id):
        vendor_id = self.vendor.get('id')
        shop_url = reverse('create-shop', kwargs={'vendor_pk': vendor_id})
        data = {
            "vendor": vendor_id,
            "email": "test@gmail.com",
            "instagram_username": instagram_username,
            "instagram_id": instagram_id,
            "province": "British Columbia",
            "city": "Vancouver",
            "address": "Berna 14",
            "preparation": 1,
            "delivery": 2
        }
        response = self.client.post(shop_url, data, format='json')
        if response.status_code != 201:
            print(f"shop response = {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data

    def test_shop_create_shipment(self):
        for index, data in enumerate(self.__correct_data_set):
            instagram_username = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            instagram_id = random.randint(123456789, 999999999)
            shop = self.create_shop(instagram_username, instagram_id)
            shop_id = shop.get('id')
            shipment_url = reverse('shop-shipment', kwargs={'shop_pk': shop_id})
            response = self.client.post(shipment_url, data, format='json')
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            print(f'response{index+1}: {response.data}')
            self.check_shop_shipment_assertion(data, response)

    def test_shop_update_shipment(self):
        instagram_username = 'test_insta'
        instagram_id = 7985614867
        shop = self.create_shop(instagram_username, instagram_id)
        shop_id = shop.get('id')

        shipment_url = reverse('shop-shipment', kwargs={'shop_pk': shop_id})

        data1 = {
            "shop": shop_id,
            "send_everywhere": True,
            "has_national_post": True,
            "has_online_delivery": True,
            "national_post": {
                "type": DeliveryPrice.DeliveryType.NATIONAL_POST,
                "base": 15000,
                "per_kilo": 2700
            },
            "online_delivery": {
                "type": DeliveryPrice.DeliveryType.ONLINE_DELIVERY,
                "base": 13000,
                "per_kilo": 2300
            },
            "city_cost": Shipment.FreeDelivery.TOTALLY_FREE,
            "country_cost": Shipment.FreeDelivery.NOT_FREE,
            "city_free_cost_from": None,
            "country_free_cost_from": None
        }
        response1 = self.client.post(shipment_url, data1, format='json')
        self.check_shop_shipment_assertion(data1, response1)

        data2 = {
            "shop": shop_id,
            "send_everywhere": False,
            "has_national_post": False,
            "has_online_delivery": True,
            "national_post": None,
            "online_delivery": {
                "type": DeliveryPrice.DeliveryType.ONLINE_DELIVERY,
                "base": 14000,
                "per_kilo": 1100
            },
            "city_cost": Shipment.FreeDelivery.TOTALLY_FREE,
            "country_cost": None,
            "city_free_cost_from": None,
            "country_free_cost_from": None
        }
        response2 = self.client.put(shipment_url, data2, format='json')
        print('after updating shipment')
        if response2.status_code != 200:
            print(response2.data)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data.get('send_everywhere'), False)
        self.assertEqual(response2.data.get('national_post'), None)
        self.assertEqual(response2.data.get('country_cost'), None)

    def check_shop_shipment_assertion(self, request_data, response):
        national_post_type = DeliveryPrice.DeliveryType.NATIONAL_POST
        online_delivery_type = DeliveryPrice.DeliveryType.ONLINE_DELIVERY

        if response.status_code != status.HTTP_201_CREATED:
            print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        if response.data.get('send_anywhere') is True:
            national_post = DeliveryPrice.objects.get(shipment=response.data['id'], type=national_post_type)
            self.assertEqual(response.data.get('national_post').get('id'), national_post.id)

        # national post checking
        if response.data.get('national_post') is None:
            self.assertEqual(request_data.get('national_post'), None)
        else:
            national_post = DeliveryPrice.objects.get(shipment=response.data['id'], type=national_post_type)
            self.assertEqual(response.data.get('national_post').get('id'), national_post.id)

        # online delivery checking
        if response.data.get('online_delivery') is None:
            self.assertEqual(request_data.get('online_delivery'), None)
        else:
            online_delivery = DeliveryPrice.objects.get(shipment=response.data['id'], type=online_delivery_type)
            self.assertEqual(response.data.get('online_delivery').get('id'), online_delivery.id)
