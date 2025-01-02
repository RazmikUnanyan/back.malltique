"""
Tests for the tags API endpoints.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from product.serializers import TagsSerializer

TAGS_URL = reverse('product:tag-list')

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



