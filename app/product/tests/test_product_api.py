"""
Test for product APIs.
"""
from decimal import Decimal  # Импортируем модуль для работы с числами с фиксированной точностью.
from itertools import product

from django.contrib.auth import get_user_model  # Импорт функции для получения текущей модели пользователя.
from django.template.defaultfilters import title
from django.test import TestCase  # Импорт класса для создания тестов.
from django.urls import reverse  # Импорт функции для генерации URL-адресов.

from rest_framework import status  # Импортируем статусы HTTP из DRF.
from rest_framework.test import APIClient  # Импорт клиента для тестирования API.

from core.models import Product  # Импорт модели рецептов.

from product.serializers import (
    ProductSerializers,
    ProductDetailSerializers,
)  # Импорт сериализатора для рецептов.

from user.tests.test_user_api import create_user  # Импорт функции для создания пользователя из тестов пользователя.

def detail_url(product_id):
    return reverse('product:product-detail', args=[product_id])

# Создаем URL для списка рецептов с помощью функции reverse.
PRODUCT_URL = reverse('product:product-list')


# Функция для создания рецепта с указанным пользователем и параметрами.
def create_product(user, **params):
    # Значения по умолчанию для полей рецепта.
    defaults = {
        'title': 'titile',  # Заголовок рецепта.
        'description': 'description',  # Описание рецепта.
        'price': "3.42",  # Цена рецепта.
        'link': '#',  # Ссылка на рецепт.
        'time_minutes': 2,  # Время приготовления в минутах.
    }

    # Обновляем значения по умолчанию, если переданы дополнительные параметры.
    defaults.update(params)

    # Создаем экземпляр рецепта в базе данных.
    product = Product.objects.create(user=user, **defaults)
    return product  # Возвращаем созданный рецепт.


def create_user(**params):
    """Create and return new user"""
    return get_user_model().objects.create_user(**params)


# Класс тестов для неавторизованных запросов к API рецептов.
class PublicProductAPITests(TestCase):
    """Test UNAUTHORIZED req"""

    def setUp(self):
        # Инициализируем клиент API для тестирования.
        self.client = APIClient()

    def test_auth_required(self):
        # Тестируем, что доступ к API рецептов требует авторизации.
        res = self.client.get(PRODUCT_URL)  # Отправляем GET-запрос.

        # Проверяем, что код ответа - 401 (неавторизован).
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# Класс тестов для авторизованных запросов к API рецептов.
class PrivateProductAPITests(TestCase):
    """Test authenticated API request"""

    def setUp(self):
        # Инициализируем клиент API для тестирования.
        self.client = APIClient()
        # Создаем пользователя для тестирования.
        self.user = create_user(email='test@example.com', password='eeeepass')
        # Аутентифицируем пользователя в API-клиенте.
        self.client.force_authenticate(self.user)

    def test_retrieve_product(self):
        """Test retrieving a list of product."""
        # Создаем два рецепта для текущего пользователя.
        create_product(user=self.user)
        create_product(user=self.user)

        # Отправляем GET-запрос на получение списка рецептов.
        res = self.client.get(PRODUCT_URL)

        # Получаем список рецептов из базы, отсортированных по ID в порядке убывания.
        product = Product.objects.all().order_by('-id')
        serializer = ProductSerializers(product, many=True)  # Сериализуем данные.

        # Проверяем, что код ответа - 200 (успешно).
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Сравниваем данные ответа с сериализованными данными.
        self.assertEqual(res.data, serializer.data)

    def test_product_limited_to_user(self):
        """Test list of product is limited to authenticated user."""
        # Создаем другого пользователя.
        other_user = create_user(email='Res@example.com', password='testpasstse')
        # Создаем рецепт для другого пользователя.
        create_product(user=other_user)
        # Создаем рецепт для текущего пользователя.
        create_product(user=self.user)

        # Отправляем GET-запрос на получение списка рецептов.
        res = self.client.get(PRODUCT_URL)

        # Получаем рецепты, принадлежащие текущему пользователю.
        product = Product.objects.filter(user=self.user)
        serializer = ProductSerializers(product, many=True)  # Сериализуем данные.

        # Проверяем, что код ответа - 200 (успешно).
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Сравниваем данные ответа с сериализованными данными.
        self.assertEqual(res.data, serializer.data)


    def test_get_product_detail(self):
        product = create_product(user=self.user)

        url = detail_url(product.id)
        res = self.client.get(url)

        serializer = ProductDetailSerializers(product)
        self.assertEqual(res.data, serializer.data)

    def test_create_product(self):
        """Test creating a product."""
        payload = {
            'title': "test create",
            'price': Decimal('2.33'),
            'description': 'test create description',
            'time_minutes': 23,
        }

        res = self.client.post(PRODUCT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(product, k), v)
        self.assertEqual(product.user, self.user)

    def test_partial_update(self):
        original_link = 'https://fmalltique.com'
        product = create_product(
            user=self.user,
            title='title',
            link=original_link
        )

        payload = {'title': "new product"}
        url=detail_url(product.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertEqual(product.title, payload['title'])
        self.assertEqual(product.link, original_link)
        self.assertEqual(product.user, self.user)




