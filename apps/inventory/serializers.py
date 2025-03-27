from rest_framework import serializers

from .models import Brand, Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        """Meta class to define the category model and fields to serialize."""

        model = Category
        fields = ["name"]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        """Meta class to define the brand model and fields to serialize."""

        model = Brand
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    category = CategorySerializer()

    class Meta:
        """Meta class to define the product model and fields to serialize."""

        model = Product
        fields = [
            "product_id",
            "name",
            "short_description",
            "long_description",
            "price",
            "stock",
        ]

    def validate_price(self, value):
        """Ensure that the product price is not below 0."""
        if value <= 0:
            msg = "Price must be greater than 0."
            raise serializers.ValidationError(msg)
        return value
