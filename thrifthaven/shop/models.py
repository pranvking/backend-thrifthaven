from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to="items/", blank=True, null=True)
    video = models.FileField(upload_to="items/videos/", blank=True, null=True)
    categories = models.ManyToManyField(Category)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    stock = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Apply depreciation logic only if offer_price not set
        if not self.offer_price:
            depreciation_rate = Decimal("0.20")  # 20% depreciation
            self.offer_price = self.price * (1 - depreciation_rate)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message[:20]}"

    def mark_as_read(self):
        self.is_read = True
        self.save()
