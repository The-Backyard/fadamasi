from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.carts.models import Cart, CartItem

from .serializers import (
    CartItemCreateSerializer,
    CartItemSerializer,
    CartItemUpdateSerializer,
    CartSerializer,
)


class CartViewSet(viewsets.GenericViewSet):
    """ViewSet for managing the authenticated user's cart."""

    permission_classes = [AllowAny]
    serializer_class = CartSerializer

    def get_queryset(self):
        """Return queryset for the current user's cart."""
        if self.request.user.is_authenticated:
            return Cart.objects.filter(user=self.request.user)

        # For guest users, use session key
        session_key = self._get_or_create_session_key()
        return Cart.objects.filter(session_key=session_key)

    def _get_or_create_session_key(self):
        """Get or create a session key for guest users."""
        if not self.request.session.session_key:
            self.request.session.create()
        return self.request.session.session_key

    def get_object(self):
        """Get or create cart for the current user."""
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            return cart

        # For guest users
        session_key = self._get_or_create_session_key()
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart

    def list(self, request):
        """Get the user's cart with all items."""
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=["delete"])
    def clear(self, request):
        """Clear all items from the cart."""
        cart = self.get_object()
        cart.items.all().delete()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def merge(self, request):
        """Merge a guest cart into the user's cart after login.

        This should be called after user authentication.
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required to merge carts."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Get the session key from the request data
        session_key = request.data.get("session_key") or request.session.session_key

        if not session_key:
            return Response(
                {"detail": "No guest cart session found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Get the guest cart
            guest_cart = Cart.objects.get(session_key=session_key)

            # Get or create the user cart
            user_cart, created = Cart.objects.get_or_create(user=request.user)

            # Merge the items
            with transaction.atomic():
                user_cart_items = {
                    (item.product, item.size, item.color): item
                    for item in user_cart.items.all()
                }

                for guest_item in guest_cart.items.all():
                    key = (guest_item.product, guest_item.size, guest_item.color)
                    user_item = user_cart_items.get(key)

                    if user_item:
                        # Update quantity
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

            serializer = self.get_serializer(user_cart)
            return Response(serializer.data)

        except Cart.DoesNotExist:
            return Response(
                {"detail": "Guest cart not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class CartItemViewSet(viewsets.GenericViewSet):
    """ViewSet for managing cart items for the authenticated user."""

    permission_classes = [AllowAny]
    serializer_class = CartItemSerializer

    def _get_or_create_session_key(self):
        """Get or create a session key for guest users."""
        if not self.request.session.session_key:
            self.request.session.create()
        return self.request.session.session_key

    def get_queryset(self):
        """Return cart items for the current user's cart (authenticated or guest)."""
        if self.request.user.is_authenticated:
            return CartItem.objects.filter(cart__user=self.request.user)

        # For guest users, use session key
        session_key = self._get_or_create_session_key()
        return CartItem.objects.filter(cart__session_key=session_key)

    def get_cart(self):
        """Get or create cart for the current user (authenticated or guest)."""
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            return cart

        # For guest users
        session_key = self._get_or_create_session_key()
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart

    def create(self, request):
        """Add an item to the cart.

        If the product already exists with the same attributes, update quantity instead.
        """
        cart = self.get_cart()
        serializer = CartItemCreateSerializer(data=request.data)

        if serializer.is_valid():
            product = serializer.validated_data["product"]
            size = serializer.validated_data.get("size")
            color = serializer.validated_data.get("color")
            quantity = serializer.validated_data.get("quantity", 1)

            # Check if item already exists in cart
            try:
                cart_item = CartItem.objects.get(
                    cart=cart,
                    product=product,
                    size=size,
                    color=color,
                )
                # Update existing item quantity
                cart_item.quantity += quantity
                cart_item.save()
                result_serializer = CartItemSerializer(cart_item)
                return Response(result_serializer.data)
            except CartItem.DoesNotExist:
                # Create new item
                with transaction.atomic():
                    cart_item = CartItem.objects.create(
                        cart=cart,
                        product=product,
                        quantity=quantity,
                        size=size,
                        color=color,
                    )
                    result_serializer = CartItemSerializer(cart_item)
                    return Response(
                        result_serializer.data,
                        status=status.HTTP_201_CREATED,
                    )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def retrieve(self, request, pk=None):
        """Get a specific cart item for the current user."""
        queryset = self.get_queryset()
        cart_item = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(cart_item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """Update a cart item (quantity, size, color)."""
        queryset = self.get_queryset()
        cart_item = get_object_or_404(queryset, pk=pk)
        serializer = CartItemUpdateSerializer(
            cart_item,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            result_serializer = CartItemSerializer(cart_item)
            return Response(result_serializer.data)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, pk=None):
        """Remove an item from the cart."""
        queryset = self.get_queryset()
        cart_item = get_object_or_404(queryset, pk=pk)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
