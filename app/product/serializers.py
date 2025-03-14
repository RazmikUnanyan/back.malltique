"""
Serializers for product API.
"""


from rest_framework import serializers

from core.models import (
    Product,
    Tag,
    ClothingSize
)


class ClothingSizeSerializer(serializers.ModelSerializer):
    """Serializer for sizes"""
    class Meta:
        model = ClothingSize
        fields = ['id', 'name']
        read_only_fields = ['id']


class TagsSerializer(serializers.ModelSerializer):
    """Serializer for tags"""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class ProductSerializers(serializers.ModelSerializer):
    """Serializers for product."""
    # tags = TagsSerializer(many=True, required=False)
    # clothing_sizes = ClothingSizeSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'youtube', 'spotify', 'image'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        clothing_sizes = validated_data.pop('clothing_sizes', [])
        product = Product.objects.create(**validated_data)
        self._get_or_create_tags(tags, product)
        self._get_or_create_clothing_sizes(clothing_sizes, product)

        return product

    def update(self, instance, validated_data):
        """Update products."""
        # tags = validated_data.pop('tags', None)
        # clothing_sizes = validated_data.pop('clothing_sizes', None)
        # if tags is not None:
        #     instance.tags.clear()
        #     self._get_or_create_tags(tags, instance)
        # if clothing_sizes is not None:
        #     instance.clothing_sizes.clear()
        #     self._get_or_create_clothing_sizes(clothing_sizes, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ProductDetailSerializers(ProductSerializers):
    """Serializers for product detail."""
    class Meta(ProductSerializers.Meta):
        fields = ProductSerializers.Meta.fields + ['description', 'image']


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to product."""

    class Meta:
        model = Product
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}
