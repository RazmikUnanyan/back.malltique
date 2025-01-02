"""
URL mapping for the product app.
"""
# This docstring explains that this file contains the URL configurations for the product app.

from django.urls import (
    path,
    include,
)
# Importing `path` and `include` to define URL patterns for the app.

from rest_framework.routers import DefaultRouter
# Importing `DefaultRouter` from Django REST Framework to automatically generate URL routes for viewsets.

from product import views
# Importing views from the `product` app to link them to the router.

router = DefaultRouter()
# Creating an instance of the DefaultRouter for automatic URL routing.

router.register('product', views.ProductViewSet)
router.register('tag', views.TagViewSet)

app_name = 'product'
# Defining the app namespace for the `product` app, useful for namespaced URL reversing.

urlpatterns = [
    path('', include(router.urls))
]
# Defining the URL patterns for the app. All routes generated by the `router` are included here.
