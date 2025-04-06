import uuid

from django.conf import settings
from django.db import models


class Order(models.Model):
    class StatusChoices(models.TextChoices):
        """Enumeration of possible order statuses."""

        PENDING = "PENDING"
        CONFIRMED = "CONFIRMED"
        CANCELLED = "CANCELLED"

    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    products = models.ManyToManyField(
        "products.Product", through="OrderItem", related_name="orders"
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return a string representation of the order."""
        return f"Order ID: {self.order_id}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        """Return a string representation of the order item."""
        return f"{self.quantity} x {self.product.name} in Order {self.order.order_id}"

    @property
    def item_subtotal(self):
        return self.product.price * self.quantity
