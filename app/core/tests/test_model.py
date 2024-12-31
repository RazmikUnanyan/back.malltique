"""
Tests for models.
"""
from decimal import Decimal

from django.test import TestCase  # Import the base class for creating tests.
from django.contrib.auth import get_user_model  # Retrieve the user model used in the project.

from core import models  # Import models from the core application.


def create_user(email="test@example.com", password='testpass123'):
    """Helper function to create a user."""
    return get_user_model().objects.create_user(email, password)


class TestModels(TestCase):  # Create a test class inheriting from TestCase.
    """Tests for models."""

    def test_create_user_with_email_successful(self):
        """Test: successfully creating a user with an email."""
        email = "test@example.com"  # Test email.
        password = "testpass11!"  # Test password.
        user = get_user_model().objects.create_user(  # Create a user with the provided email and password.
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)  # Verify that the user's email matches the provided one.
        self.assertTrue(user.check_password(password))  # Verify that the password is set correctly.

    def test_new_user_email_normalized(self):
        """Test: email is normalized upon user creation."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:  # For each sample, check normalization.
            user = get_user_model().objects.create_user(email, 'sample123')  # Create a user.
            self.assertEqual(user.email, expected)  # Verify that the email is normalized correctly.

    def test_new_user_without_email_raises_error(self):
        """Test: creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):  # Expect a ValueError if no email is provided.
            get_user_model().objects.create_user('', 'sample123')  # Attempt to create a user without an email.

    def test_create_superuser(self):
        """Test: successfully creating a superuser."""
        user = get_user_model().objects.create_superuser(  # Create a superuser.
            'test4@example.com',
            '123'
        )

        self.assertTrue(user.is_superuser)  # Verify the user is a superuser.
        self.assertTrue(user.is_staff)  # Verify the user has staff status.

    def test_create_product(self):
        """Test: successfully creating a product."""
        user = get_user_model().objects.create_user(  # Create a user for the product.
            'test@example.com',
            'pass123',
        )

        product = models.Product.objects.create(  # Create a product object with specified attributes.
            user=user,
            title='simple product name',  # Product title.
            description='simple test',  # Product description.
            price=Decimal('5.5'),  # Product price.
            time_minutes=5,  # Preparation time in minutes.
            link="////"
        )

        self.assertEqual(str(product), product.title)  # Verify the string representation matches the product title.

    def test_create_tag(self):
        """Test: successfully creating a tag."""
        user = create_user()  # Create a user.
        tag = models.Tag.objects.create(user=user, name="Tag1")  # Create a tag associated with the user.

        self.assertEqual(str(tag), tag.name)  # Verify the string representation matches the tag name.
