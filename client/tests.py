from random import random, randint

from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

# Create your tests here.
from client.models import Customer
from client.views import CustomAuthToken


class LoginTest(TestCase):
    TEST_LOGIN = True

    def setUp(self):
        self.factory = RequestFactory()
        self.PHONE = '00000000'
        for i in range(len(self.PHONE)):
            self.PHONE = self.PHONE[:i] + str(randint(0, 9)) + self.PHONE[i + 1:]
        if self.TEST_LOGIN:
            user = User.objects.create(username=self.PHONE, password='')
            customer = Customer()
            customer.user = user
            customer.phone = self.PHONE
            customer.snn = self.PHONE
            customer.firstName = 'abas'
            customer.lastName = 'gholami'
            customer.save()

    def test_login(self):
        request = self.factory.get('client/login/{}'.format(self.PHONE))
        response = CustomAuthToken.as_view()(request, self.PHONE)
        self.assertEqual(response.status_code, 200)
        request = self.factory.post('client/login/', data={'phone': self.PHONE, 'code': 1234})
        response = CustomAuthToken.as_view()(request)
        self.assertEqual(response.status_code, 200)
        print(response.data['token'])

    def test_signup(self):
        request = self.factory.get('client/login/{}'.format(self.PHONE))
        response = CustomAuthToken.as_view()(request, self.PHONE)
        self.assertEqual(response.status_code, 200)
        request = self.factory.post('client/login/', data={'phone': self.PHONE, 'code': 1234})
        response = CustomAuthToken.as_view()(request)
        self.assertEqual(response.status_code, 200)
        print(response.data['token'])
