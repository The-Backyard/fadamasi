import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Cart(models.Model):
    """Cart model that stores user cart information."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name=_("User"),
        null=True,
        blank=True,
    )
    session_key = models.CharField(
        max_length=255,
        default="",
        blank=True,
        verbose_name=_("Session Key"),
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        """Metadata for the Cart model."""

        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")
        ordering = ["-updated"]
        constraints = [
            # Ensure cart has either a user or a session key
            models.CheckConstraint(
                check=(
                    models.Q(user__isnull=False) | models.Q(session_key__isnull=False)
                ),
                name="cart_has_user_or_session",
            )
        ]

    def __str__(self):
        """Return a string representation of the cart."""
        if self.user:
            return f"Cart: {self.user.email}"
        return f"Guest Cart: {self.session_key[:8]}..."

    @property
    def total_price(self):
        """Calculate total price of all items in cart."""
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        """Calculate total number of items in cart."""
        return sum(item.quantity for item in self.items.all())

    @property
    def is_guest_cart(self):
        """Check if this is a guest cart."""
        return self.user is None


class CartItem(models.Model):
    """Cart item that associates products with a cart."""

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Cart"),
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        verbose_name=_("Product"),
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Quantity"),
    )
    size = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name=_("Size"),
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name=_("Color"),
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        """Metadata for the CartItem model."""

        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")
        ordering = ["-created"]
        # Ensure a product with same size and color combo can't be added twice
        # Instead, quantity should be updated
        unique_together = ["cart", "product", "size", "color"]

    def __str__(self):
        """Return a string representation of the cart item."""
        return f"{self.quantity} x {self.product.name} in {self.cart}"

    @property
    def subtotal(self):
        """Calculate price for this cart item."""
        return Decimal(self.product.price) * self.quantity
