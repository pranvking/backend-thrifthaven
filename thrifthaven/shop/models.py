from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField(blank=True, null=True)  # <- needed by algo
    image = models.ImageField(upload_to="items/", blank=True, null=True)
    video = models.FileField(upload_to="items/videos/", blank=True, null=True)
    categories = models.ManyToManyField(Category)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)   # becomes True when user accepts offer
    stock = models.BooleanField(default=False)      # optional “sold” flag
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # <- new
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Notification(models.Model):
    TYPE_CHOICES = [
        ("INFO", "Info"),
        ("OFFER", "Offer"),
        ("APPROVED", "Approved"),
        ("DECLINED", "Declined"),
        ("SOLD", "Sold"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="INFO")
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} - {self.message[:20]}"
