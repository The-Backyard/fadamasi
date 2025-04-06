from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to="products/", blank=True)

    def __str__(self) -> str:
        """Return a string representation of the product."""
        return self.name

    @property
    def in_stock(self):
        return self.stock > 0
