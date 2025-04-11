from rest_framework import serializers

from apps.carts.models import Cart, CartItem
from apps.products.api.serializers import ProductDetailSerializer
from apps.products.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items with product details."""

    product_details = ProductDetailSerializer(
        source="product",
        read_only=True,
    )
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        help_text="Subtotal price for this item (quantity x price)",
    )

    class Meta:
        """Meta class for CartItemSerializer."""

        model = CartItem
        fields = [
            "id",
            "product",
            "product_details",
            "quantity",
            "size",
            "color",
            "subtotal",
            "created",
            "updated",
        ]
        read_only_fields = [
            "id",
            "created",
            "updated",
            "subtotal",
        ]

    def validate_product(self, value):
        """Validate that product exists and is active."""
        try:
            return Product.objects.get(pk=value.id, is_active=True)
        except Product.DoesNotExist:
            error_message = f"Product with ID {value.id} does not exist or is inactive."
            raise serializers.ValidationError(error_message) from None

    def validate_quantity(self, value):
        """Validate quantity is positive."""
        if value <= 0:
            error_message = "Quantity must be greater than zero."
            raise serializers.ValidationError(error_message)
        return value

    def validate(self, data):
        """Additional validations for product availability."""
        product = data.get("product")
        size = data.get("size")
        color = data.get("color")
        quantity = data.get("quantity", 1)

        # Check if product has size/color options and validate them
        if product.has_sizes and not size:
            raise serializers.ValidationError(
                {"size": "Size selection is required for this product."}
            )

        if product.has_colors and not color:
            raise serializers.ValidationError(
                {"color": "Color selection is required for this product."}
            )

        # Check stock availability (assuming Product model has stock tracking)
        if hasattr(product, "stock") and product.stock < quantity:
            raise serializers.ValidationError(
                {"quantity": f"Only {product.stock} items available in stock."}
            )

        return data


class CartItemCreateSerializer(CartItemSerializer):
    """Serializer for creating cart items with minimal fields."""

    class Meta(CartItemSerializer.Meta):
        """Meta class for CartItemCreateSerializer."""

        fields = [
            "product",
            "quantity",
            "size",
            "color",
        ]


class CartItemUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating cart item quantity."""

    class Meta:
        """Meta class for CartItemUpdateSerializer."""

        model = CartItem
        fields = [
            "quantity",
            "size",
            "color",
        ]


class CartSerializer(serializers.ModelSerializer):
    """Cart serializer that includes cart items."""

    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        help_text="Total price of all items in cart",
    )
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        """Meta class for CartSerializer."""

        model = Cart
        fields = [
            "id",
            "user",
            "items",
            "total_price",
            "total_items",
            "created",
            "updated",
        ]
        read_only_fields = [
            "id",
            "user",
            "created",
            "updated",
        ]
