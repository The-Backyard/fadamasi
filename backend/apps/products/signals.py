from django.db.models import Sum
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import Product, ProductColor, ProductImage, ProductSize


@receiver(post_save, sender=ProductImage)
def ensure_one_featured_image(sender, instance, created, **kwargs):
    """Ensures that each product has at least one featured image.

    If there's only one image, it's automatically set as featured.
    """
    if created and instance.is_featured:
        # If a new featured image was created, make sure it's the only featured one
        ProductImage.objects.filter(product=instance.product, is_featured=True).exclude(
            id=instance.id
        ).update(is_featured=False)

    # If this is the only image for the product, make it featured
    if created and instance.product.images.count() == 1:
        instance.is_featured = True
        instance.save(update_fields=["is_featured"])

    # If no featured image exists after setting this one to not featured,
    # set the first available image as featured
    if (
        not instance.is_featured
        and not instance.product.images.filter(is_featured=True).exists()
    ):
        first_image = instance.product.images.first()
        if first_image:
            first_image.is_featured = True
            first_image.save(update_fields=["is_featured"])


@receiver(post_delete, sender=ProductImage)
def update_featured_on_delete(sender, instance, **kwargs):
    """When a featured image is deleted, sets another image as featured if available."""
    if instance.is_featured and instance.product.images.exists():
        first_image = instance.product.images.first()
        if first_image:
            first_image.is_featured = True
            first_image.save(update_fields=["is_featured"])


@receiver(post_save, sender=ProductColor)
@receiver(post_delete, sender=ProductColor)
def update_product_availability_on_color_change(sender, instance, **kwargs):
    """Updates product availability based on color inventory changes."""
    product = instance.product

    # Check if any colors are available
    colors_available = product.productcolor_set.filter(
        is_available=True, stock_quantity__gt=0
    ).exists()

    # If product has colors but none are available, mark product as unavailable
    if product.productcolor_set.exists() and not colors_available:
        if product.is_available:
            product.is_available = False
            product.save(update_fields=["is_available"])
    # If product has available colors but is marked unavailable, update it
    elif colors_available and not product.is_available:
        product.is_available = True
        product.save(update_fields=["is_available"])


@receiver(post_save, sender=ProductSize)
@receiver(post_delete, sender=ProductSize)
def update_product_availability_on_size_change(sender, instance, **kwargs):
    """Updates product availability based on size inventory changes."""
    product = instance.product

    # Check if any sizes are available
    sizes_available = product.productsize_set.filter(
        is_available=True, stock_quantity__gt=0
    ).exists()

    # If product has sizes but none are available, mark product as unavailable
    if product.productsize_set.exists() and not sizes_available:
        if product.is_available:
            product.is_available = False
            product.save(update_fields=["is_available"])
    # If product has available sizes but is marked unavailable, update it
    elif sizes_available and not product.is_available:
        product.is_available = True
        product.save(update_fields=["is_available"])


@receiver(pre_save, sender=Product)
def update_stock_quantity(sender, instance, **kwargs):
    """Updates the total stock_quantity based on color and size quantities.

    This is a backup calculation in case specific color/size tracking is used.
    """
    # Only run this for existing products
    if instance.pk:
        # Calculate total from color inventory if available
        color_total = (
            ProductColor.objects.filter(product=instance).aggregate(
                total=Sum("stock_quantity")
            )["total"]
            or 0
        )

        # Calculate total from size inventory if available
        size_total = (
            ProductSize.objects.filter(product=instance).aggregate(
                total=Sum("stock_quantity")
            )["total"]
            or 0
        )

        # Use the most appropriate total
        if color_total > 0 and size_total > 0:
            # If both are tracked, use the minimum to be safe
            instance.stock_quantity = min(color_total, size_total)
        elif color_total > 0:
            instance.stock_quantity = color_total
        elif size_total > 0:
            instance.stock_quantity = size_total
        # Otherwise, keep the manually set quantity
