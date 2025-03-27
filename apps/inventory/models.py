import uuid

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    category_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
    )
    name = models.CharField(
        "name",
        max_length=50,
        unique=True,
    )
    parent = TreeForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        """Meta class to define the order of the category model."""

        order_insertion_by = ["name"]

    def __str__(self):
        """String representation of the category instance."""
        return self.name


class Brand(models.Model):
    brand_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
    )
    name = models.CharField(
        "name",
        max_length=50,
        unique=True,
    )

    def __str__(self):
        """String representation of the brand instance."""
        return self.name


class Product(models.Model):
    product_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
    )
    name = models.CharField(
        "name",
        max_length=50,
    )
    short_description = models.CharField(max_length=255)
    long_description = models.TextField(blank=True)
    brand = models.ForeignKey(
        "Brand",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    category = TreeForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    stock = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """String representation of the product instance."""
        return self.name

    @property
    def in_stock(self):
        return self.stock > 0
