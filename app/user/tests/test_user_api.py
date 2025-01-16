"""
Tests for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREAT_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):

    def setUp(self):
        # Set up the API client.
        self.client = APIClient()

    def test_create_user_success(self):
        # Test for successful user creation.
        payload = {
            'email': 'text@exaple.com',
            'password': 'tesdtpass343e',
            'name': 'Test Name',
        }
        res = self.client.post(CREAT_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        # Test for error when trying to create a user with an existing email.
        payload = {
            'email': 'text@exaple.com',
            'password': 'testpass343e',
            'name': 'Test Name',
        }
        create_user(**payload)  # Create a user.
        res = self.client.post(CREAT_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_to_short_error(self):
        """Test for an error if the password is shorter than 5 characters."""
        payload = {
            'email': 'text@exaple.com',
            'password': 'ss',  # Specify a too-short password.
            'name': 'Test Name',
        }
        res = self.client.post(CREAT_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test for generating a token for the user."""
        user_details = {
            'email': "test@example.com",
            'password': "123pass",
            'name': "Test Name",
        }
        create_user(**user_details)  # Create a user.

        payload = {
            'password': user_details['password'],
            'email': user_details['email'],
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_token_bad_credentials(self):
        """Test for error with incorrect credentials."""
        create_user(email="test@example.com", password="pass")

        payload = {
            'email': "test@example.com",
            'password': "123pass",
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_creat_token_blank_password(self):
        # Test for error with an empty password.
        create_user(email="test@example.com", password="pass")

        payload = {
            'email': "test@example.com",
            'password': "",  # Provide an empty password.
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# Tests for authorized requests to the user API.
class PrivateUserApiTest(TestCase):

    def setUp(self):
        # Create a user and authenticate the client.
        self.user = create_user(
            email="test@example.com",
            password='testpass123',
            name='test name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        # Test for successful profile retrieval.
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test that POST requests are not allowed for this endpoint."""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        # Test for successful user profile update.
        payload = {
            'name': 'Update name',  # New name.
            'password': 'Update pass',  # New password.
        }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
