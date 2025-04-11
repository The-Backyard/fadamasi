from django.db import transaction
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.api.pagination import StandardResultsSetPagination
from apps.accounts.api.permissions import IsAdmin
from apps.products.models import (
    Category,
    Color,
    Product,
    ProductColor,
    ProductImage,
    ProductSize,
    Size,
)

from .filters import ProductFilter
from .serializers import (
    CategorySerializer,
    ColorSerializer,
    ProductColorCreateUpdateSerializer,
    ProductCreateSerializer,
    ProductDetailSerializer,
    ProductImageCreateSerializer,
    ProductListSerializer,
    ProductSizeCreateUpdateSerializer,
    SizeSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product categories.

    Only accessible by admin users.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin]
    lookup_field = "slug"


class ColorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product colors.

    Only accessible by admin users.
    """

    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [IsAdmin]


class SizeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product sizes.

    Only accessible by admin users.
    """

    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    permission_classes = [IsAdmin]


class ProductAdminViewSet(viewsets.ModelViewSet):
    """ViewSet for managing products.

    Only accessible by admin users.
    """

    queryset = Product.objects.all()
    permission_classes = [IsAdmin]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "create":
            return ProductCreateSerializer
        return ProductDetailSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create a new product."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        # Return the full product details
        response_serializer = ProductDetailSerializer(
            product, context={"request": request}
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="upload-image")
    @transaction.atomic
    def upload_image(self, request, slug=None):
        """Upload product images."""
        product = self.get_object()
        serializer = ProductImageCreateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(product=product)
            return Response(
                {"message": "Image uploaded successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True, methods=["delete"], url_path="delete-image/(?P<image_id>[^/.]+)"
    )
    @transaction.atomic
    def delete_image(self, request, slug=None, image_id=None):
        """Delete a product image."""
        product = self.get_object()
        try:
            image = product.images.get(id=image_id)
            image.delete()
            return Response(
                {"message": "Image deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except ProductImage.DoesNotExist:
            return Response(
                {"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=["post"], url_path="add-color")
    @transaction.atomic
    def add_color(self, request, slug=None):
        """Add color option to a product."""
        product = self.get_object()
        serializer = ProductColorCreateUpdateSerializer(data=request.data)

        if serializer.is_valid():
            # Check if this color already exists for the product
            color = serializer.validated_data["color"]
            product_color, created = ProductColor.objects.get_or_create(
                product=product,
                color=color,
                defaults={
                    "stock_quantity": serializer.validated_data.get(
                        "stock_quantity", 0
                    ),
                    "is_available": serializer.validated_data.get("is_available", True),
                },
            )

            # If not created, update the existing one
            if not created:
                product_color.stock_quantity = serializer.validated_data.get(
                    "stock_quantity", product_color.stock_quantity
                )
                product_color.is_available = serializer.validated_data.get(
                    "is_available", product_color.is_available
                )
                product_color.save()

            return Response(
                {"message": f"Color {'added' if created else 'updated'} successfully"},
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True, methods=["delete"], url_path="remove-color/(?P<color_id>[^/.]+)"
    )
    @transaction.atomic
    def remove_color(self, request, slug=None, color_id=None):
        """Remove color option from a product."""
        product = self.get_object()
        try:
            product_color = ProductColor.objects.get(product=product, color_id=color_id)
            product_color.delete()
            return Response(
                {"message": "Color removed successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except ProductColor.DoesNotExist:
            return Response(
                {"error": "Color not found for this product"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["post"], url_path="add-size")
    @transaction.atomic
    def add_size(self, request, slug=None):
        """Add size option to a product."""
        product = self.get_object()
        serializer = ProductSizeCreateUpdateSerializer(data=request.data)

        if serializer.is_valid():
            # Check if this size already exists for the product
            size = serializer.validated_data["size"]
            product_size, created = ProductSize.objects.get_or_create(
                product=product,
                size=size,
                defaults={
                    "stock_quantity": serializer.validated_data.get(
                        "stock_quantity", 0
                    ),
                    "is_available": serializer.validated_data.get("is_available", True),
                },
            )

            # If not created, update the existing one
            if not created:
                product_size.stock_quantity = serializer.validated_data.get(
                    "stock_quantity", product_size.stock_quantity
                )
                product_size.is_available = serializer.validated_data.get(
                    "is_available", product_size.is_available
                )
                product_size.save()

            return Response(
                {"message": f"Size {'added' if created else 'updated'} successfully"},
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["delete"], url_path="remove-size/(?P<size_id>[^/.]+)")
    @transaction.atomic
    def remove_size(self, request, slug=None, size_id=None):
        """Remove size option from a product."""
        product = self.get_object()
        try:
            product_size = ProductSize.objects.get(product=product, size_id=size_id)
            product_size.delete()
            return Response(
                {"message": "Size removed successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except ProductSize.DoesNotExist:
            return Response(
                {"error": "Size not found for this product"},
                status=status.HTTP_404_NOT_FOUND,
            )


class PublicCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for public access to product categories."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"


class PublicProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for public access to products.

    Supports filtering, searching and pagination.
    """

    queryset = Product.objects.prefetch_related("images", "category").all()
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    filterset_class = ProductFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = [
        "name",
        "description",
        "category__name",
    ]
    ordering_fields = ["price", "created", "name"]
    ordering = ["-created"]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Annotate with additional data for potential performance optimizations
        queryset = queryset.annotate(
            image_count=Count("images", distinct=True),
            color_count=Count("colors", distinct=True),
            size_count=Count("sizes", distinct=True),
        )

        if self.action == "list":
            # For list view, optimize the query to avoid unnecessary joins
            queryset = queryset.filter(is_available=True)
            queryset = queryset.select_related("category")
            queryset = queryset.prefetch_related("images")

        return queryset
