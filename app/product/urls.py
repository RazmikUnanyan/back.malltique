"""
URL mapping for the product app.
"""

from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from product import views

router = DefaultRouter()
router.register('product', views.ProductViewSet)
router.register('tag', views.TagViewSet)
router.register('clothing_sizes',
                views.ClothingSizeViewSet,
                basename='clothing_sizes'
                )

app_name = 'product'

urlpatterns = [
    path('', include(router.urls))
]
