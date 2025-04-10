import re

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class UsernameValidator:
    """Validator for usernames."""

    def __call__(self, value):
        # Check min length
        if len(value) < 3:
            raise serializers.ValidationError(
                _("Username must be at least 3 characters long.")
            )

        # Check if alphanumeric with underscores and hyphens
        if not re.match(r"^[a-zA-Z0-9_\-]+$", value):
            raise serializers.ValidationError(
                _(
                    "Username can only contain letters, numbers, underscores and hyphens."
                )
            )

        return value


class PhoneNumberValidator:
    """Validator for phone numbers."""

    def __call__(self, value):
        if value and not re.match(r"^\+?[0-9]{10,15}$", value):
            raise serializers.ValidationError(
                _("Phone number must be 10-15 digits, optionally starting with +.")
            )
        return value
