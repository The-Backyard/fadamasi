from rest_framework import serializers

from apps.orders.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name")
    product_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        source="product.price",
    )

    class Meta:
        """Meta options for the Order items serializer."""

        model = OrderItem
        fields = [
            "product_name",
            "product_price",
            "quantity",
            "item_subtotal",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name="total")

    def total(self, obj):
        order_items = obj.items.all()
        return sum(order_item.item_subtotal for order_item in order_items)

    class Meta:
        """Meta options for the Order serializer."""

        model = Order
        fields = [
            "order_id",
            "created",
            "user",
            "status",
            "items",
            "total_price",
        ]
