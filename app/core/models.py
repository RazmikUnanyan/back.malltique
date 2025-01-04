"""
Database models.
"""
from django.conf import settings  # Import project settings for Django.
from django.db import models  # Import base module for working with models.
from django.contrib.auth.models import (  # Import base classes for working with users.
    AbstractBaseUser,  # Base class for custom user models.
    BaseUserManager,  # Manager for handling user objects.
    PermissionsMixin,  # Adds support for permissions and groups.
)
from django.db.models import CharField  # Import a field for text data.


class UserManager(BaseUserManager):  # Custom manager for the User model.
    """Manager for handling user objects."""

    def create_user(self, email, password=None, **extra_fields):
        """Creates, saves, and returns a new user."""
        if not email:  # Check if an email is provided.
            raise ValueError('A user must have an email address.')  # Raise an error if email is missing.
        user = self.model(email=self.normalize_email(email), **extra_fields)  # Create a model instance with a normalized email.
        user.set_password(password)  # Set the user's password.
        user.save(using=self._db)  # Save the user to the database.

        return user  # Return the created user.

    def create_superuser(self, email, password):
        """Creates and returns a superuser."""
        user = self.create_user(email, password)  # Create a regular user.
        user.is_staff = True  # Grant staff status (admin access).
        user.is_superuser = True  # Grant superuser status.
        user.save(using=self._db)  # Save changes to the database.

        return user  # Return the superuser.


class User(AbstractBaseUser, PermissionsMixin):  # Create a custom user model inheriting the base user class.
    """User model in the system."""
    email = models.EmailField(max_length=255, unique=True)  # Email field, required and unique.
    name = models.CharField(max_length=255)  # Name field for the user.
    is_active = models.BooleanField(default=True)  # User active status.
    is_staff = models.BooleanField(default=False)  # Determines if the user has staff privileges (admin access).

    objects = UserManager()  # Attach the custom user manager.

    USERNAME_FIELD = 'email'  # Specify that email is used for authentication.


class Product(models.Model):  # Model for storing product data.
    """Product objects."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Link the product to a user through the custom user model.
        on_delete=models.CASCADE,  # Delete all associated products if the user is deleted.
    )
    title = models.CharField(max_length=100)  # Product title.
    description = models.TextField(blank=True)  # Product description, optional field.
    time_minutes = models.IntegerField()  # Preparation time in minutes.
    price = models.DecimalField(max_digits=5, decimal_places=2)  # Product price, accurate to two decimal places.
    link = models.CharField(max_length=100, blank=True)  # Link to the product, optional field.
    tags = models.ManyToManyField('Tag')  # Many-to-many relationship with the Tag model.
    clothing_sizes = models.ManyToManyField('ClothingSize')  # Many-to-many relationship with the Size model.

    def __str__(self):
        """Returns the string representation of the object (product title)."""
        return self.title  # Display the product title.


class Tag(models.Model):  # Model for tags associated with products.
    """Tag objects."""
    name = models.CharField(max_length=225)  # Tag name.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Link the tag to a user through the custom user model.
        on_delete=models.CASCADE,  # Delete all associated tags if the user is deleted.
    )

    def __str__(self):
        return self.name  # Display the tag name.


class ClothingSize(models.Model):
    """Size objects."""
    name = models.CharField(max_length=10)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
