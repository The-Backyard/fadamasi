from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=11, blank=True, default="")

    def __str__(self) -> str:
        """Return a string representation of the profile."""
        return f"Profile of {self.user.username}"
