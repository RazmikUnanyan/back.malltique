"""
View for product.
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Product,
    Tag,
    ClothingSize
)
from product import serializers

@extend_schema_view(
    # Decorator to extend the schema for this view, enabling customization of API documentation.
    list=extend_schema(
        # Specifies schema customization for the `list` action of the view.
        parameters=[
            # Defines additional query parameters for the API endpoint.
            OpenApiParameter(
                'tags',  # Name of the query parameter.
                OpenApiTypes.STR,  # Specifies the type of the parameter as a string.
                description="Comma separated list of IDs to filter"  # Description of how to use the parameter.
            ),
            OpenApiParameter(
                'clothing_sizes',  # Name of the query parameter.
                OpenApiTypes.STR,  # Specifies the type of the parameter as a string.
                description="Comma separated list of clothing_sizes IDs to filter"  # Description of how to use the parameter.
            )
        ]
    )
)

class ProductViewSet(viewsets.ModelViewSet):
    """Views for manage product APIs."""
    serializer_class = serializers.ProductDetailSerializers
    queryset = Product.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list strings to integers"""
        return [int(str_id) for str_id in qs.split(',')]


    def get_queryset(self):
        """Retrieve product for authentication user."""
        tags = self.request.query_params.get('tags')
        clothing_sizes = self.request.query_params.get('clothing_sizes')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if clothing_sizes:
            clothing_sizes_ids = self._params_to_ints(clothing_sizes)
            queryset = queryset.filter(clothing_sizes__id__in=clothing_sizes_ids)

        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.ProductSerializers
        elif self.action == 'upload_image':
            return serializers.ProductImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create new product"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to product."""
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseProductAttrViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Base viewset for product attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')



class TagViewSet(BaseProductAttrViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagsSerializer
    queryset = Tag.objects.all()


class ClothingSizeViewSet(BaseProductAttrViewSet):
    """Manage sizes in the database."""
    serializer_class = serializers.ClothingSizeSerializer
    queryset = ClothingSize.objects.all()
