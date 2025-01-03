"""
Test for product APIs.
"""
from decimal import Decimal  # Импортируем модуль для работы с числами с фиксированной точностью.
from itertools import product
from os.path import exists

from django.contrib.auth import get_user_model  # Импорт функции для получения текущей модели пользователя.

from django.test import TestCase  # Импорт класса для создания тестов.
from django.urls import reverse  # Импорт функции для генерации URL-адресов.

from rest_framework import status  # Импортируем статусы HTTP из DRF.
from rest_framework.test import APIClient  # Импорт клиента для тестирования API.

from core.models import (
    Product,
    Tag,
)

from product.serializers import (
    ProductSerializers,
    ProductDetailSerializers,
)  # Импорт сериализаторов для продуктов.

from user.tests.test_user_api import create_user  # Импорт функции для создания пользователя из тестов пользователя.

def detail_url(product_id):
    """Generate and return a product detail URL."""
    return reverse('product:product-detail', args=[product_id])

# Создаем URL для списка продуктов с помощью функции reverse.
PRODUCT_URL = reverse('product:product-list')

def create_product(user, **params):
    """Create and return a new product."""
    defaults = {
        'title': 'title',  # Заголовок продукта.
        'description': 'description',  # Описание продукта.
        'price': "3.42",  # Цена продукта.
        'link': '#',  # Ссылка на продукт.
        'time_minutes': 2,  # Время подготовки продукта в минутах.
    }
    defaults.update(params)
    return Product.objects.create(user=user, **defaults)

def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)

class PublicProductAPITests(TestCase):
    """Test UNAUTHORIZED req"""

    def setUp(self):
        """Set up the test client."""
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required to access products."""
        res = self.client.get(PRODUCT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateProductAPITests(TestCase):
    """Test AUTHENTICATED API requests."""

    def setUp(self):
        """Set up the test client and authenticate user."""
        self.client = APIClient()
        self.user = create_user(email='test@example.com', password='eeeepass')
        self.client.force_authenticate(self.user)

    def test_retrieve_product(self):
        """Test retrieving a list of products."""
        create_product(user=self.user)
        create_product(user=self.user)

        res = self.client.get(PRODUCT_URL)
        products = Product.objects.all().order_by('-id')
        serializer = ProductSerializers(products, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_product_limited_to_user(self):
        """Test that products are limited to the authenticated user."""
        other_user = create_user(email='other@example.com', password='testpass')
        create_product(user=other_user)
        create_product(user=self.user)

        res = self.client.get(PRODUCT_URL)
        products = Product.objects.filter(user=self.user)
        serializer = ProductSerializers(products, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_product_detail(self):
        """Test retrieving a product's detail."""
        product = create_product(user=self.user)
        url = detail_url(product.id)
        res = self.client.get(url)

        serializer = ProductDetailSerializers(product)
        self.assertEqual(res.data, serializer.data)

    def test_create_product(self):
        """Test creating a product."""
        payload = {
            'title': "Test Product",
            'price': Decimal('2.33'),
            'description': 'Test description',
            'time_minutes': 10,
        }
        res = self.client.post(PRODUCT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(product, k), v)
        self.assertEqual(product.user, self.user)

    def test_partial_update(self):
        """Test partially updating a product."""
        product = create_product(user=self.user, title='Original Title', link='https://example.com')
        payload = {'title': 'Updated Title'}
        url = detail_url(product.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertEqual(product.title, payload['title'])

    def test_full_update(self):
        """Test updating a product with PUT."""
        product = create_product(user=self.user, title='Original Title', link='https://example.com')
        payload = {
            'title': 'Updated Title',
            'link': 'https://example.com/updated',
            'description': 'Updated Description',
            'time_minutes': 5,
            'price': Decimal('5.00'),
        }
        url = detail_url(product.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(product, k), v)

    def test_update_user_returns_error(self):
        """Test changing the product user results in an error."""
        new_user = create_user(email='newuser@example.com', password='testpass')
        product = create_product(user=self.user)
        payload = {'user': new_user.id}
        url = detail_url(product.id)
        self.client.patch(url, payload)

        product.refresh_from_db()
        self.assertEqual(product.user, self.user)

    def test_delete_product(self):
        """Test deleting a product."""
        product = create_product(user=self.user)
        url = detail_url(product.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=product.id).exists())

    def test_delete_other_user_product(self):
        """Test attempting to delete another user's product results in an error."""
        other_user = create_user(email='other@example.com', password='testpass')
        product = create_product(user=other_user)
        url = detail_url(product.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Product.objects.filter(id=product.id).exists())

    def test_create_product_with_new_tags(self):
        payload = {
            'title': 'Updated Title',
            'link': 'https://example.com/updated',
            'description': 'Updated Description',
            'time_minutes': 5,
            'price': Decimal('5.00'),
            'tags': [{'name': "tad 1"}, {'name': 'tag 2'}]
        }

        res = self.client.post(
            PRODUCT_URL,
            payload,
            format="json"
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        products = Product.objects.filter(user=self.user)
        self.assertEqual(products.count(), 1)
        product = products[0]
        self.assertEqual(product.tags.count(), 2)
        for tag in payload['tags']:
            exists = product.tags.filter(name=tag['name'], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_product_existing_tags(self):
        tag_indian = Tag.objects.create(user=self.user, name='indian')
        payload = {
            'title': 'Updated Title',
            'link': 'https://example.com/updated',
            'description': 'Updated Description',
            'time_minutes': 5,
            'price': Decimal('5.00'),
            'tags': [{'name': "indian"}, {'name': 'Breakfast'}]
        }

        res = self.client.post(PRODUCT_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        products = Product.objects.filter(user=self.user)
        self.assertEqual(products.count(), 1)
        product = products[0]
        self.assertEqual(product.tags.count(), 2)
        self.assertIn(tag_indian, product.tags.all())
        for tag in payload['tags']:
            exists = product.tags.filter(name=tag['name'], user=self.user).exists()
            self.assertTrue(exists)