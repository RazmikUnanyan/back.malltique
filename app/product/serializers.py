"""
Serializers for product API.
"""
from itertools import product

from rest_framework import serializers

from core.models import (
    Product,
    Tag
)

class TagsSerializer(serializers.ModelSerializer):
    """Serializer for tags"""
    class Meta:
        model=Tag
        fields=['id', 'name']
        read_only_fields=['id']


class ProductSerializers(serializers.ModelSerializer):
    """Serializers for product."""
    tags = TagsSerializer(many=True, required=False)

    class Meta:
        model=Product
        fields=['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields=['id']

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        product = Product.objects.create(**validated_data)
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(user=auth_user, **tag)
            product.tags.add(tag_obj)

        return product

class ProductDetailSerializers(ProductSerializers):
    """Serializers for product detail."""
    class Meta(ProductSerializers.Meta):
        fields=ProductSerializers.Meta.fields + ['description']
