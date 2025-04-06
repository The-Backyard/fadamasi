from rest_framework import serializers

from apps.products.models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        """Meta options for the Product model."""

        model = Product
        fields = [
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


class ProductInfoSerializer(serializers.Serializer):
    # get all products, count of products, max price
    products = ProductSerializer(many=True)
    count = serializers.IntegerField()
    max_price = serializers.FloatField()
