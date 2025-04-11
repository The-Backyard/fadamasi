import uuid

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, default="")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        """Metadata for the Category model."""

        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        """Return a string representation of the category."""
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Color(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    color_code = models.CharField(
        max_length=10,
        blank=True,
        default="",
    )

    def __str__(self):
        """Return a string representation of the color."""
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Size(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="E.g., 'Small', 'Medium'",
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="E.g., 'S', 'M'",
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
    )

    class Meta:
        """Returns metadata for the Size model."""

        ordering = ["name"]

    def __str__(self):
        """Return string representation for the Size model."""
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    class GenderChoices(models.TextChoices):
        """Enumeration for gender choices."""

        MALE = "M", _("Male")
        FEMALE = "F", _("Female")
        UNISEX = "U", _("Unisex")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField()

    # Price information
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )

    # Inventory information
    stock_quantity = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)

    # Optional relations
    colors = models.ManyToManyField(
        Color,
        through="ProductColor",
        blank=True,
    )
    sizes = models.ManyToManyField(
        Size,
        through="ProductSize",
        blank=True,
    )

    # Product specifications
    gender = models.CharField(
        max_length=1,
        choices=GenderChoices.choices,
        default=GenderChoices.UNISEX,
    )
    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Weight specification in Kg."),
    )

    is_featured = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        """Metadata for the Product model."""

        ordering = ["-created"]

    def __str__(self):
        """String representation for the product."""
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

            # Ensure slug uniqueness
            original_slug = self.slug
            counter = 1
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    @property
    def current_price(self):
        """Returns the current effective price."""
        if self.discount_price:
            return self.discount_price
        return self.price

    @property
    def discount_percentage(self):
        """Calculate discount percentage if discount price is available."""
        if self.discount_price and self.price > 0:
            discount = ((self.price - self.discount_price) / self.price) * 100
            return round(discount, 2)
        return 0


class ProductImage(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="products/%Y/%m/")
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )
    is_featured = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Metadata for the ProductImage model."""

        ordering = ["-is_featured", "created"]

    def __str__(self):
        """Return a string representation of the product image."""
        return f"{self.product.name} - {'Featured' if self.is_featured else 'Gallery'}"

    def save(self, *args, **kwargs):
        # Ensure only one featured image per product
        if self.is_featured:
            ProductImage.objects.filter(
                product=self.product,
                is_featured=True,
            ).update(is_featured=False)
        super().save(*args, **kwargs)


class ProductColor(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)

    class Meta:
        """Metadata for the ProductColor model."""

        unique_together = ("product", "color")

    def __str__(self):
        """Return a string representation of the product color."""
        return f"{self.product.name} - {self.color.name}"


class ProductSize(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)

    class Meta:
        """Metadata for the ProductSize model."""

        unique_together = ("product", "size")

    def __str__(self):
        """Return a string representation of the product size."""
        return f"{self.product.name} - {self.size.name}"
