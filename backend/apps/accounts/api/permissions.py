from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Permission check for admin users."""

    message = "Only admin users are allowed to perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsCustomer(permissions.BasePermission):
    """Permission check for customer users."""

    message = "Only customers are allowed to perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_customer


class IsAdminOrReadOnly(permissions.BasePermission):
    """Permission to allow only admin users to create, update, or delete objects.

    Regular users can only read.
    """

    message = "Only admin users can modify content."

    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to admin users
        return request.user.is_authenticated and request.user.is_admin
