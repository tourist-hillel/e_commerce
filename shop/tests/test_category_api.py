from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from shop.models import Category


class TestCategoryListAPI(APITestCase):

    def setUp(self):
        self.root = Category.objects.create(
            name='Electronics', slug='elec'
        )
        self.child = Category.objects.create(
            name='Phones', slug='phones', parent=self.root
        )
        self.inactive = Category.objects.create(
            name='Inactive', slug='inactive', is_active=False
        )

    def test_returns_http_200(self):
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_response_is_paginated(self):
    #     response = self.client.get('/api/categories/')
    #     self.assertIn('count', response.data)
    #     self.assertIn('results', response.data)
