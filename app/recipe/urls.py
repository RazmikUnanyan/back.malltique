"""
URL mapping for the recipe app.
"""
# This docstring explains that this file contains the URL configurations for the recipe app.

from django.urls import (
    path,
    include,
)
# Importing `path` and `include` to define URL patterns for the app.

from rest_framework.routers import DefaultRouter
# Importing `DefaultRouter` from Django REST Framework to automatically generate URL routes for viewsets.

from recipe import views
# Importing views from the `recipe` app to link them to the router.

router = DefaultRouter()
# Creating an instance of the DefaultRouter for automatic URL routing.

router.register('recipes', views.RecipeViewSet)
# Registering the `RecipeViewSet` with the router under the `recipes` endpoint.

app_name = 'recipe'
# Defining the app namespace for the `recipe` app, useful for namespaced URL reversing.

urlpatterns = [
    path('', include(router.urls))
]
# Defining the URL patterns for the app. All routes generated by the `router` are included here.
