from django.contrib.auth.signals import user_logged_in
from django.db import transaction
from django.dispatch import receiver
from django.utils.deprecation import MiddlewareMixin

from .models import Cart, CartItem


class CartMiddleware(MiddlewareMixin):
    """Middleware to ensure session is initialized for cart usage."""

    def process_request(self, request):
        # Initialize session if needed
        if not request.session.session_key:
            request.session.create()
        return


@receiver(user_logged_in)
def merge_carts_on_login(sender, request, user, **kwargs):
    """When a user logs in, merge any guest cart into their user cart."""
    if not request or not request.session.session_key:
        return

    session_key = request.session.session_key

    try:
        # Check if there is a guest cart with this session
        guest_cart = Cart.objects.get(session_key=session_key, user__isnull=True)

        # Get or create the user cart
        user_cart, created = Cart.objects.get_or_create(user=user)

        # Merge the items
        with transaction.atomic():
            # Preload user cart items into a dictionary for quick lookup
            user_cart_items = {
                (item.product_id, item.size, item.color): item
                for item in CartItem.objects.filter(cart=user_cart)
            }

            for guest_item in guest_cart.items.all():
                key = (guest_item.product_id, guest_item.size, guest_item.color)
                if key in user_cart_items:
                    # Update quantity if item exists in user cart
                    user_item = user_cart_items[key]
                    user_item.quantity += guest_item.quantity
                    user_item.save()
                else:
                    # Create new item in user cart
                    CartItem.objects.create(
                        cart=user_cart,
                        product=guest_item.product,
                        quantity=guest_item.quantity,
                        size=guest_item.size,
                        color=guest_item.color,
                    )

            # Delete the guest cart
            guest_cart.delete()

    except Cart.DoesNotExist:
        # No guest cart exists, nothing to merge
        pass
