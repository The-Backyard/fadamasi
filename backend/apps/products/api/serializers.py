from rest_framework import serializers

from products.models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        """Meta options for the Product model."""

        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "stock",
            "image",
        ]

    def validate_price(self, value):
        """Check the the price is not 0 or below."""
        if value <= 0:
            msg = "Price must be greater than 0."
            raise serializers.ValidationError(msg)
        return value
