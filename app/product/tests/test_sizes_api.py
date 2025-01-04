"""
Test for the sizes API.
"""
from linecache import cache

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Size

from product.serializers import SizesSerializer

SIZE_URL = reverse('product:size-list')


def create_user(email="test@example.com", password="<PASSWORD>"):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email=email, password=password)

class PublicSizeAPITests(TestCase):
    """Test unauthenticated size API access."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required."""
        res = self.client.get(SIZE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



class PrivateSizeAPITests(TestCase):
    """Test authenticated sizes API access."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_sizes(self):
        """Test retrieving a list of size."""
        Size.objects.create(user=self.user, name='S')
        Size.objects.create(user=self.user, name='M')

        res = self.client.get(SIZE_URL)

        sizes = Size.objects.all().order_by('-name')
        serializer = SizesSerializer(sizes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_sizes_limited_to_user(self):
        user2 = create_user(email="test2@exaple.com")
        Size.objects.create(user=user2, name='XXL')
        size = Size.objects.create(user=self.user, name='XL')

        res = self.client.get(SIZE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], size.name)
        self.assertEqual(res.data[0]['id'], size.id)