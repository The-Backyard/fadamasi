import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    """Creates a Custom user model.

    Custom User model where email is the unique identifier
    instead of username for authentication.
    """

    CUSTOMER = "customer"
    ADMIN = "admin"

    ROLE_CHOICES = (
        (CUSTOMER, _("Customer")),
        (ADMIN, _("Admin")),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
    )
    email = models.EmailField(
        _("email address"),
        unique=True,
    )
    first_name = models.CharField(
        _("first name"),
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        _("last name"),
        max_length=150,
        blank=True,
    )
    phone_number = models.CharField(
        _("phone number"),
        max_length=15,
        blank=True,
        default="",
        help_text=_("International format preferred: +1234567890"),
    )
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    role = models.CharField(
        _("role"),
        max_length=20,
        choices=ROLE_CHOICES,
        default=CUSTOMER,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    class Meta:
        """Meta options for CustomUser model."""

        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]

    def __str__(self):
        """String representation of the custom user."""
        return f"{self.email} ({self.username})"

    @property
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_customer(self):
        """Check if user has customer role."""
        return self.role == self.CUSTOMER

    @property
    def full_name(self):
        """Return the user's full name."""
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username
