"""
Test for the sizes API.
"""
from  decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    ClothingSize,
    Product,
)

from product.serializers import ClothingSizeSerializer

CLOTHING_SIZE_URL = reverse('product:clothing_sizes-list')

def detail_url(clothing_size_id):
    """Generate and return a clothing_sizes detail URL."""
    return reverse('product:clothing_sizes-detail', args=[clothing_size_id])

def create_user(email="test@example.com", password="<PASSWORD>"):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email=email, password=password)

class PublicClothingSizeAPITests(TestCase):
    """Test unauthenticated size API access."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required."""
        res = self.client.get(CLOTHING_SIZE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



class PrivateClothingSizeAPITests(TestCase):
    """Test authenticated Clothing Size API access."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_clothing_size(self):
        """Test retrieving a list of size."""
        ClothingSize.objects.create(user=self.user, name='S')
        ClothingSize.objects.create(user=self.user, name='M')

        res = self.client.get(CLOTHING_SIZE_URL)

        clothing_sizes = ClothingSize.objects.all().order_by('-name')
        serializer = ClothingSizeSerializer(clothing_sizes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_clothing_size_limited_to_user(self):
        user2 = create_user(email="test2@exaple.com")
        ClothingSize.objects.create(user=user2, name='XXL')
        clothing_sizes = ClothingSize.objects.create(user=self.user, name='XL')

        res = self.client.get(CLOTHING_SIZE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], clothing_sizes.name)
        self.assertEqual(res.data[0]['id'], clothing_sizes.id)


    def test_update_clothing_size(self):
        """Test update size."""
        clothing_sizes = ClothingSize.objects.create(user=self.user, name="L")

        payload = {'name': 'XXL'}
        url=detail_url(clothing_sizes.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        clothing_sizes.refresh_from_db()
        self.assertEqual(clothing_sizes.name, payload['name'])

    def test_delete_clothing_size(self):
        """Test delete size."""
        clothing_sizes = ClothingSize.objects.create(user=self.user, name="tag")
        url = detail_url(clothing_sizes.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        sizes = ClothingSize.objects.filter(id=clothing_sizes.id)
        self.assertFalse(sizes.exists())

    def test_filter_clothing_size_assigned_product(self):
        cs1= ClothingSize.objects.create(user=self.user, name="L")
        cs2= ClothingSize.objects.create(user=self.user, name="XL")
        product = Product.objects.create(
            user=self.user,
            title= 'Updated Title',
            time_minutes = 5,
            price=Decimal('5.00'),
        )

        product.clothing_sizes.add(cs1)

        res = self.client.get(CLOTHING_SIZE_URL, {'assigned_only': 1})

        s1 = ClothingSizeSerializer(cs1)
        s2 = ClothingSizeSerializer(cs2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_clothing_size_unique(self):
        cs1 = ClothingSize.objects.create(user=self.user, name="L")
        ClothingSize.objects.create(user=self.user, name="XL")
        product1 = Product.objects.create(
            user=self.user,
            title='1',
            time_minutes=5,
            price=Decimal('5.00'),
        )

        product2 = Product.objects.create(
            user=self.user,
            title='2',
            time_minutes=5,
            price=Decimal('5.00'),
        )

        product1.clothing_sizes.add(cs1)
        product2.clothing_sizes.add(cs1)

        res = self.client.get(CLOTHING_SIZE_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
