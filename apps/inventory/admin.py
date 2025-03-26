from django.contrib import admin

from .models import Brand, Category, Product

admin.site.register([Brand, Category, Product])
