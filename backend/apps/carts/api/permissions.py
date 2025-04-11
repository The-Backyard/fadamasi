from rest_framework import permissions


class IsCartOwner(permissions.BasePermission):
    """Custom permission to ensure only cart owners can access their cart."""

    message = "You do not have permission to access this cart."

    def has_object_permission(self, request, view, obj):
        # Check if the user is the owner of the cart
        return obj.user == request.user


class IsCartItemOwner(permissions.BasePermission):
    """Custom permission to ensure only cart item owners can access their cart items."""

    message = "You do not have permission to access this cart item."

    def has_object_permission(self, request, view, obj):
        # Check if the user is the owner of the cart that contains this item
        return obj.cart.user == request.user
