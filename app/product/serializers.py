"""
Serializers for product API.
"""
from itertools import product

from rest_framework import serializers

from core.models import (
    Product,
    Tag,
    ClothingSize
)

class ClothingSizeSerializer(serializers.ModelSerializer):
    """Serializer for sizes"""
    class Meta:
        model=ClothingSize
        fields=['id', 'name']
        read_only_fields=['id']

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

    def _get_or_create_tags(self, tags, product):
        """handle creating or getting tags."""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(user=auth_user, **tag)
            product.tags.add(tag_obj)

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        product = Product.objects.create(**validated_data)
        self._get_or_create_tags(tags, product)

        return product

    def update(self, instance, validated_data):
        """Update products."""
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return  instance






class ProductDetailSerializers(ProductSerializers):
    """Serializers for product detail."""
    class Meta(ProductSerializers.Meta):
        fields=ProductSerializers.Meta.fields + ['description']
