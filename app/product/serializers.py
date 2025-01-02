"""
Serializers for product API.
"""

from rest_framework import serializers

from core.models import (
    Product,
    Tag
)

class ProductSerializers(serializers.ModelSerializer):
    """Serializers for product."""
    class Meta:
        model=Product
        fields=['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields=['id']


class ProductDetailSerializers(ProductSerializers):
    """Serializers for product detail."""
    class Meta(ProductSerializers.Meta):
        fields=ProductSerializers.Meta.fields + ['description']


class TagsSerializer(serializers.ModelSerializer):
    """Serializer for tags"""

    class Meta:
        model=Tag
        fields=['id', 'name']
        read_only_fields=['id']