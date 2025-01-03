"""
View for product.
"""
from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Product,
    Tag,
)
from product import serializers


class ProductViewSet(viewsets.ModelViewSet):
    """Views for manage product APIs."""
    serializer_class = serializers.ProductDetailSerializers
    queryset = Product.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve product for authentication user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ProductSerializers

        return self.serializer_class

    def perform_create(self, serializer):
        """Create new product"""
        serializer.save(user=self.request.user)


class TagViewSet(mixins.DestroyModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagsSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter tags for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')




