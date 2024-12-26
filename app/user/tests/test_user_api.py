"""
Tests for the user API.
"""
from django.test import TestCase  # Importing the module for creating tests in Django.
from django.contrib.auth import get_user_model  # Importing the function to work with the user model.
from django.urls import reverse  # Importing the function to get a URL by its name.

from rest_framework.test import APIClient  # Importing the class for testing APIs.
from rest_framework import status  # Importing HTTP response statuses.

# Define URLs for creating a user, obtaining a token, and accessing the user profile.
CREAT_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

# Helper function to create a user.
def create_user(**params):
    return get_user_model().objects.create_user(**params)

# Tests for public requests to the user API.
class PublicUserApiTests(TestCase):

    def setUp(self):
        # Set up the API client.
        self.client = APIClient()

    def test_create_user_success(self):
        # Test for successful user creation.
        payload = {
            'email': 'text@exaple.com',  # Input data: email, password, and name.
            'password': 'tesdtpass343e',
            'name': 'Test Name',
        }
        res = self.client.post(CREAT_USER_URL, payload)  # Send a request to create a user.

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  # Verify successful creation status.
        user = get_user_model().objects.get(email=payload['email'])  # Check that the user was created.
        self.assertTrue(user.check_password(payload['password']))  # Ensure the password was set correctly.
        self.assertNotIn('password', res.data)  # Ensure the password is not returned in the response.

    def test_user_with_email_exists_error(self):
        # Test for error when trying to create a user with an existing email.
        payload = {
            'email': 'text@exaple.com',
            'password': 'testpass343e',
            'name': 'Test Name',
        }
        create_user(**payload)  # Create a user.
        res = self.client.post(CREAT_USER_URL, payload)  # Try to create the user again.

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # Verify that an error was returned.

    def test_password_to_short_error(self):
        """Test for an error if the password is shorter than 5 characters."""
        payload = {
            'email': 'text@exaple.com',
            'password': 'ss',  # Specify a too-short password.
            'name': 'Test Name',
        }
        res = self.client.post(CREAT_USER_URL, payload)  # Try to create a user.

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # Verify that an error was returned.
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()  # Ensure the user was not created.
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
            'password': user_details['password'],  # Provide correct credentials.
            'email': user_details['email'],
        }
        res = self.client.post(TOKEN_URL, payload)  # Attempt to obtain a token.
        self.assertIn('token', res.data)  # Ensure the token is present in the response.
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_token_bad_credentials(self):
        """Test for error with incorrect credentials."""
        create_user(email="test@example.com", password="pass")  # Create a user.

        payload = {
            'email': "test@example.com",
            'password': "123pass",  # Provide incorrect password.
        }
        res = self.client.post(TOKEN_URL, payload)  # Attempt to obtain a token.

        self.assertNotIn('token', res.data)  # Ensure the token is not present in the response.
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_creat_token_blank_password(self):
        # Test for error with an empty password.
        create_user(email="test@example.com", password="pass")  # Create a user.

        payload = {
            'email': "test@example.com",
            'password': "",  # Provide an empty password.
        }
        res = self.client.post(TOKEN_URL, payload)  # Attempt to obtain a token.

        self.assertNotIn('token', res.data)  # Ensure the token is not present.
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        # Test for error when trying to access the profile without authorization.
        res = self.client.get(ME_URL)  # Attempt to get profile data.

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)  # Verify that an error was returned.

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

        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Verify successful status.
        self.assertEqual(res.data, {  # Verify that the profile data is correct.
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test that POST requests are not allowed for this endpoint."""
        res = self.client.post(ME_URL, {})  # Attempt to send a POST request.

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)  # Verify that the method is not allowed.

    def test_update_user_profile(self):
        # Test for successful user profile update.
        payload = {
            'name': 'Update name',  # New name.
            'password': 'Update pass',  # New password.
        }
        res = self.client.patch(ME_URL, payload)  # Send a PATCH request to update the profile.

        self.user.refresh_from_db()  # Refresh the user data from the database.
        self.assertEqual(self.user.name, payload['name'])  # Verify the name was updated.
        self.assertTrue(self.user.check_password(payload['password']))  # Verify the password was updated.
        self.assertEqual(res.status_code, status.HTTP_200_OK)
