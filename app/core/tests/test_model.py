"""
Tests for models.
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email="test@example.com", password='testpass123'):
    """Helper function to create a user."""
    return get_user_model().objects.create_user(email, password)


class TestModels(TestCase):
    """Tests for models."""

    def test_create_user_with_email_successful(self):
        """Test: successfully creating a user with an email."""
        email = "test@example.com"
        password = "testpass11!"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test: email is normalized upon user creation."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test: creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'sample123')

    def test_create_superuser(self):
        """Test: successfully creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test4@example.com',
            '123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_product(self):
        """Test: successfully creating a product."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'pass123',
        )

        product = models.Product.objects.create(
            user=user,
            title='simple product name',
            description='simple test',
            price=Decimal('5.5'),
            time_minutes=5,
            link="////"
        )

        self.assertEqual(str(product), product.title)

    def test_create_tag(self):
        """Test: successfully creating a tag."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name="Tag1")

        self.assertEqual(str(tag), tag.name)

    def test_product_clothing_size(self):
        """Test: successfully creating a sizes."""
        user = create_user()
        clothing_size = models.ClothingSize.objects.create(user=user, name="XL")

        self.assertEqual(str(clothing_size), clothing_size.name)