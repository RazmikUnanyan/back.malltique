"""
Test for product APIs.
"""
from cgitb import reset
from decimal import Decimal  # Импортируем модуль для работы с числами с фиксированной точностью.
import tempfile
import os
from fileinput import filename

from PIL import Image

from django.contrib.auth import get_user_model  # Импорт функции для получения текущей модели пользователя.

from django.test import TestCase  # Импорт класса для создания тестов.
from django.urls import reverse  # Импорт функции для генерации URL-адресов.

from rest_framework import status  # Импортируем статусы HTTP из DRF.
from rest_framework.test import APIClient  # Импорт клиента для тестирования API.

from core.models import (
    Product,
    Tag,
    ClothingSize
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

def image_upload_url(product_id):
    """Generate and return a product image URL."""
    return reverse('product:product-upload-image', args=[product_id])

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

    def test_create_tags_on_update(self):
        """Test creating tags when updating a product."""
        product = create_product(user=self.user)

        payload = {'tags': [{'name': 'tag 123'}]}
        url = detail_url(product.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='tag 123')
        self.assertIn(new_tag, product.tags.all())

    def test_update_product_assign_tags(self):
        """Test assigning an existing tag when updating a product."""
        tag_breakfast = Tag.objects.create(user=self.user, name='breakfast')
        product = create_product(user=self.user)
        product.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(product.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, product.tags.all())
        self.assertNotIn(tag_breakfast, product.tags.all())

    def test_clear_product_tags(self):
        """Test clearing a product tags."""
        tag = Tag.objects.create(user=self.user, name='tag clearing')
        product = create_product(user=self.user)
        product.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(product.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(product.tags.count(), 0)

    def test_create_product_with_new_clothing_sizes(self):
        payload = {
            'title': 'Updated Title',
            'time_minutes': 5,
            'price': Decimal('5.00'),
            'tags': [{'name': 'L'}, {'name': 'XL'}],
            'clothing_sizes': [{'name': 'L'}, {'name': 'XL'}],
        }

        res = self.client.post(PRODUCT_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        products = Product.objects.filter(user=self.user)
        self.assertEqual(products.count(), 1)
        product = products[0]
        self.assertEqual(product.clothing_sizes.count(), 2)
        for clothing_size in payload['clothing_sizes']:
            exists = product.clothing_sizes.filter(
                name=clothing_size['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_product_existing_clothing_size(self):
        clothing_size_xl = ClothingSize.objects.create(user=self.user, name='XL')
        payload = {
            'title': 'Updated Title',
            'link': 'https://example.com/updated',
            'description': 'Updated Description',
            'time_minutes': 5,
            'price': Decimal('5.00'),
            'tags': [{'name': "ssXL"}, {'name': 'aaaL'}],
            'clothing_sizes': [{'name': "XL"}, {'name': 'L'}]
        }
        res = self.client.post(PRODUCT_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        products = Product.objects.filter(user=self.user)
        self.assertEqual(products.count(), 1)
        product = products[0]
        self.assertEqual(product.clothing_sizes.count(), 2)
        self.assertIn(clothing_size_xl, product.clothing_sizes.all())
        for clothing_size in payload['clothing_sizes']:
            exists = product.clothing_sizes.filter(
                name=clothing_size['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_clothing_size_on_update(self):
        """Test creating clothing_size when updating a product."""
        product = create_product(user=self.user)

        payload = {'clothing_sizes': [{'name': 'XXL'}]}
        url = detail_url(product.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_clothing_size = ClothingSize.objects.get(user=self.user, name='XXL')
        self.assertIn(new_clothing_size, product.clothing_sizes.all())

    def test_update_product_assign_clothing_size(self):
        """Test assigning an existing clothing_size when updating a product."""
        size_L = ClothingSize.objects.create(user=self.user, name='L')
        product = create_product(user=self.user)
        product.clothing_sizes.add(size_L)

        size_XL = ClothingSize.objects.create(user=self.user, name='XL')
        payload = {'clothing_sizes': [{'name': 'XL'}]}
        url = detail_url(product.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(size_XL, product.clothing_sizes.all())
        self.assertNotIn(size_L, product.clothing_sizes.all())

    def test_clear_product_clothing_size(self):
        """Test clearing a product clothing_size."""
        size = ClothingSize.objects.create(user=self.user, name='S')
        product = create_product(user=self.user)
        product.clothing_sizes.add(size)

        payload = {'clothing_sizes': []}
        url = detail_url(product.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(product.clothing_sizes.count(), 0)

    def test_filter_by_tags(self):
        p1 = create_product(user=self.user, title='1')
        p2 = create_product(user=self.user, title='2')
        tag1 = Tag.objects.create(user=self.user, name='T1')
        tag2 = Tag.objects.create(user=self.user, name='T2')

        p1.tags.add(tag1)
        p2.tags.add(tag2)
        p3 = create_product(user=self.user, title='3')

        params = {'tags': f'{tag1.id}, {tag2.id}'}
        res = self.client.get(PRODUCT_URL, params)

        s1 = ProductSerializers(p1)
        s2 = ProductSerializers(p2)
        s3 = ProductSerializers(p3)

        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)

    def test_filter_by_clothing_sizes(self):
        p1 = create_product(user=self.user, title='1')
        p2 = create_product(user=self.user, title='2')
        clothing_sizes1 = ClothingSize.objects.create(user=self.user, name='T1')
        clothing_sizes2 = ClothingSize.objects.create(user=self.user, name='T2')

        p1.clothing_sizes.add(clothing_sizes1)
        p2.clothing_sizes.add(clothing_sizes2)
        p3 = create_product(user=self.user, title='3')

        params = {'clothing_sizes': f'{clothing_sizes1.id}, {clothing_sizes2.id}'}
        res = self.client.get(PRODUCT_URL, params)

        s1 = ProductSerializers(p1)
        s2 = ProductSerializers(p2)
        s3 = ProductSerializers(p3)

        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)



class ImageUploadTest(TestCase):
    """Test for the image upload api"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='test@example.com', password='eeeepass')
        self.client.force_authenticate(self.user)
        self.product = create_product(user=self.user)

    def tearDown(self):
        self.product.image.delete()

    def test_upload_image(self):
        # Создаем URL для загрузки изображения, связанный с продуктом по его ID
        url = image_upload_url(self.product.id)

        # Создаем временный файл с расширением .jpg для тестового изображения
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            # Создаем простое изображение 10x10 пикселей в формате RGB
            img = Image.new('RGB', (10, 10))
            # Сохраняем изображение во временный файл в формате JPEG
            img.save(image_file, format='JPEG')
            # Перемещаем указатель файла в начало для последующего чтения
            image_file.seek(0)
            # Формируем payload с изображением для отправки
            payload = {'image': image_file}
            # Отправляем POST-запрос на сервер с изображением в формате multipart
            res = self.client.post(url, payload, format='multipart')

        # Обновляем объект продукта из базы данных
        self.product.refresh_from_db()

        # Проверяем, что сервер вернул статус 200 OK
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Убеждаемся, что в ответе присутствует ключ 'image'
        self.assertIn('image', res.data)
        # Проверяем, что файл изображения был успешно сохранен по указанному пути
        self.assertTrue(os.path.exists(self.product.image.path))


    def test_upload_image_bad_request(self):
        url = image_upload_url(self.product.id)
        payload = {'image': 'notanimage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)



