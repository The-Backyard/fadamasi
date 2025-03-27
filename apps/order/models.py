import uuid

from django.conf import settings
from django.db import models


class Order(models.Model):
    class StatusChoice(models.TextChoices):
        """Delivery status for an Order instance."""

        PENDING = "PE", "Pending"
        CONFIRMED = "CO", "Confirmed"
        CANCELLED = "CA", "Cancelled"

    order_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=2,
        choices=StatusChoice.choices,
        default=StatusChoice.PENDING,
    )
    products = models.ManyToManyField(
        "inventory.Product",
        through="OrderItem",
        related_name="orders",
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """String representation of the order instance."""
        return f"Order {self.order_id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey("inventory.Product", on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """String representation of the order item instance."""
        return f"{self.quantity} x {self.product.name} in Order {self.order.order_id}"

    @property
    def item_subtotal(self):
        return self.product * self.quantity
