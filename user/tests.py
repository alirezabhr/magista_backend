from django.test import TestCase, Client
from django.urls import reverse

# Create your tests here.


class UserApiTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user_url = reverse('user-detail')
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')

        self.user1_phone = "09171110022"
        self.user1_password = "password123"

        self.create_user(self.user1_phone, self.user1_password)

    def create_user(self, phone, password):
        data = {
            'phone': phone,
            'password': password,
        }
        response = self.client.post(path=self.signup_url, data=data)
        self.assertEqual(response.status_code, 201)

    def test_signup(self):
        data = {
            'phone': self.user1_phone,
            'password': self.user1_password,
        }
        response = self.client.post(path=self.signup_url, data=data)
        self.assertEqual(response.status_code, 400)

        data = {
            'phone': '09171001001',
            'password': 'test_password',
        }
        response = self.client.post(path=self.signup_url, data=data)
        self.assertEqual(response.status_code, 201)

    def test_login(self):
        data = {
            'phone': self.user1_phone,
            'password': self.user1_password,
        }
        response = self.client.post(path=self.login_url, data=data)
        self.assertEqual(response.status_code, 200)

        data = {
            'phone': self.user1_phone,
            'password': "test_password",
        }
        response = self.client.post(path=self.login_url, data=data)
        self.assertEqual(response.status_code, 400)

        data = {
            'phone': "phone_test",
            'password': "password_test",
        }
        response = self.client.post(path=self.login_url, data=data)
        self.assertEqual(response.status_code, 400)
