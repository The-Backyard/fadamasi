from rest_framework import serializers

from apps.products.models import (
    Category,
    Color,
    Product,
    ProductColor,
    ProductImage,
    ProductSize,
    Size,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        """Metadata for the CategorySerializer."""

        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
        ]
        read_only_fields = ["slug"]


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        """Metadata for the CategorySerializer."""

        model = Color
        fields = [
            "id",
            "name",
            "color_code",
            "slug",
        ]
        read_only_fields = ["slug"]


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        """Metadata for the SizeSerializer."""

        model = Size
        fields = [
            "id",
            "name",
            "code",
            "slug",
        ]
        read_only_fields = ["slug"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        """Metadata for the ProductImageSerializer."""

        model = ProductImage
        fields = ["id", "image", "alt_text", "is_featured"]


class ProductColorSerializer(serializers.ModelSerializer):
    color = ColorSerializer(read_only=True)
    color_id = serializers.PrimaryKeyRelatedField(
        queryset=Color.objects.all(), write_only=True, source="color"
    )

    class Meta:
        """Metadata for the ProductColorSerializer."""

        model = ProductColor
        fields = ["id", "color", "color_id", "stock_quantity", "is_available"]


class ProductSizeSerializer(serializers.ModelSerializer):
    size = SizeSerializer(read_only=True)
    size_id = serializers.PrimaryKeyRelatedField(
        queryset=Size.objects.all(),
        write_only=True,
        source="size",
    )

    class Meta:
        """Metadata for the ProductSizeSerializer."""

        model = ProductSize
        fields = ["id", "size", "size_id", "stock_quantity", "is_available"]


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    featured_image = serializers.SerializerMethodField()
    discount_percentage = serializers.FloatField(read_only=True)

    class Meta:
        """Metadata for the ProductListSerializer."""

        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "category",
            "sku",
            "price",
            "discount_price",
            "discount_percentage",
            "is_available",
            "is_featured",
            "featured_image",
            "created",
        ]

    def get_featured_image(self, obj):
        featured_image = obj.images.filter(is_featured=True).first()
        if featured_image:
            return self.context["request"].build_absolute_uri(featured_image.image.url)
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        source="category",
    )
    images = ProductImageSerializer(many=True, read_only=True)
    product_colors = ProductColorSerializer(
        source="productcolor_set",
        many=True,
        read_only=True,
    )
    product_sizes = ProductSizeSerializer(
        source="productsize_set",
        many=True,
        read_only=True,
    )
    discount_percentage = serializers.FloatField(read_only=True)

    class Meta:
        """Metadata for the ProductDetailSerializer."""

        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "category",
            "category_id",
            "description",
            "gender",
            "price",
            "discount_price",
            "discount_percentage",
            "stock_quantity",
            "is_available",
            "is_featured",
            "sku",
            "weight",
            "images",
            "product_colors",
            "product_sizes",
            "created",
            "updated",
        ]
        read_only_fields = ["slug", "discount_percentage"]


class ProductCreateSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
    )

    # Add fields for colors and sizes
    colors_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
    )

    sizes_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
    )

    class Meta:
        """Metadata for the ProductCreateSerializer."""

        model = Product
        fields = [
            "name",
            "category_id",
            "sku",
            "description",
            "gender",
            "price",
            "discount_price",
            "stock_quantity",
            "is_available",
            "weight",
            "is_featured",
            "colors_data",
            "sizes_data",
        ]

    def validate_colors_data(self, colors_data):
        """Validate that all color_ids exist in the database."""
        if colors_data:
            color_ids = [
                color_item.get("color_id")
                for color_item in colors_data
                if "color_id" in color_item
            ]

            # Check if any color_id is missing
            if any(not color_id for color_id in color_ids):
                error_message = "color_id is required for each color item"
                raise serializers.ValidationError(error_message)

            # Validate all color IDs exist
            existing_colors = Color.objects.filter(id__in=color_ids)
            if len(existing_colors) != len(color_ids):
                found_ids = {str(color.id) for color in existing_colors}
                missing_ids = [
                    color_id for color_id in color_ids if str(color_id) not in found_ids
                ]
                error_message = f"Colors with ids {missing_ids} do not exist"
                raise serializers.ValidationError(error_message)

            # Validate stock_quantity is non-negative
            for item in colors_data:
                stock_quantity = item.get("stock_quantity")
                if stock_quantity is not None and stock_quantity < 0:
                    error_message = "stock_quantity must be non-negative"
                    raise serializers.ValidationError(error_message)

    def validate_sizes_data(self, sizes_data):
        """Validate that all size_ids exist in the database."""
        if sizes_data:
            size_ids = [
                size_item.get("size_id")
                for size_item in sizes_data
                if "size_id" in size_item
            ]

            # Check if any size_id is missing
            if any(not size_id for size_id in size_ids):
                error_message = "size_id is required for each size item"
                raise serializers.ValidationError(error_message)

            # Validate all size IDs exist
            existing_sizes = Size.objects.filter(id__in=size_ids)
            if len(existing_sizes) != len(size_ids):
                found_ids = {str(size.id) for size in existing_sizes}
                missing_ids = [
                    size_id for size_id in size_ids if str(size_id) not in found_ids
                ]
                error_message = f"Sizes with ids {missing_ids} do not exist"
                raise serializers.ValidationError(error_message)

            # Validate stock_quantity is non-negative
            for item in sizes_data:
                stock_quantity = item.get("stock_quantity")
                if stock_quantity is not None and stock_quantity < 0:
                    error_message = "stock_quantity must be non-negative"
                    raise serializers.ValidationError(error_message)

        return sizes_data

    def create(self, validated_data):
        # Extract colors and sizes data
        colors_data = validated_data.pop("colors_data", [])
        sizes_data = validated_data.pop("sizes_data", [])

        # Create the product
        product = Product.objects.create(**validated_data)

        # Create ProductColor objects
        for color_item in colors_data:
            color_id = color_item.get("color_id")
            stock_quantity = color_item.get("stock_quantity", 0)
            is_available = color_item.get("is_available", True)

            color = Color.objects.get(id=color_id)
            ProductColor.objects.create(
                product=product,
                color=color,
                stock_quantity=stock_quantity,
                is_available=is_available,
            )

        # Create ProductSize objects
        for size_item in sizes_data:
            size_id = size_item.get("size_id")
            stock_quantity = size_item.get("stock_quantity", 0)
            is_available = size_item.get("is_available", True)

            size = Size.objects.get(id=size_id)
            ProductSize.objects.create(
                product=product,
                size=size,
                stock_quantity=stock_quantity,
                is_available=is_available,
            )

        return product


class ProductImageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        """Metadata for the ProductImageSerializer."""

        model = ProductImage
        fields = ["image", "alt_text", "is_featured"]


class ProductColorCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        """Metadata for the ProductColorSerializer."""

        model = ProductColor
        fields = ["color", "stock_quantity", "is_available"]


class ProductSizeCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        """Metadata for the ProductSizeSerializer."""

        model = ProductSize
        fields = ["size", "stock_quantity", "is_available"]
