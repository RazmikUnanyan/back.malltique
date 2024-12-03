"""
Test for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


class TestModels(TestCase):
    """Test models."""

    def test_email_user_with_successfull(self):
        """Test creating a user with an email is successfull."""
        email = "test@example.com"
        password = "testpass"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))