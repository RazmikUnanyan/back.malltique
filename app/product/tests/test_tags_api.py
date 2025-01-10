"""
Tests for the tags API endpoints.
"""
from  decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Tag,
    Product,
)

from product.serializers import TagsSerializer

TAGS_URL = reverse('product:tag-list')

def detail_url(tag_id):
    """Generate and return a tag detail URL."""
    return reverse('product:tag-detail', args=[tag_id])


def create_user(email="test@example.com", password="<PASSWORD>"):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email=email, password=password)

class PublicTagsAPITests(TestCase):
    """Test unauthenticated tags API access."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required."""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsAPITests(TestCase):
    """Test authenticated tags API access."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags."""
        Tag.objects.create(user=self.user, name='Test Tag')
        Tag.objects.create(user=self.user, name='Test Tag 2')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagsSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test is limited to user."""
        user2 = create_user(email="test2@exaple.com")
        Tag.objects.create(user=user2, name='Test Tag')
        tag = Tag.objects.create(user=self.user, name='Test Tag 23')

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test update tag."""
        tag = Tag.objects.create(user=self.user, name="tag")

        payload = {'name': 'new tag'}
        url=detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test delete tag."""
        tag = Tag.objects.create(user=self.user, name="tag")
        url = detail_url(tag.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(id=tag.id)
        self.assertFalse(tags.exists())

    def test_filter_tag_assigned_product(self):
        tag1= Tag.objects.create(user=self.user, name="tag1")
        tag2= Tag.objects.create(user=self.user, name="tag2")
        product = Product.objects.create(
            user=self.user,
            title= 'tag',
            time_minutes = 1,
            price=Decimal('1.00'),
        )

        product.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        s1 = TagsSerializer(tag1)
        s2 = TagsSerializer(tag2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_clothing_size_unique(self):
        tag = Tag.objects.create(user=self.user, name="L=tag")
        Tag.objects.create(user=self.user, name="tag2")
        product1 = Product.objects.create(
            user=self.user,
            title='12',
            time_minutes=2,
            price=Decimal('2.00'),
        )

        product2 = Product.objects.create(
            user=self.user,
            title='21',
            time_minutes=53,
            price=Decimal('53.00'),
        )

        product1.tags.add(tag)
        product2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)




