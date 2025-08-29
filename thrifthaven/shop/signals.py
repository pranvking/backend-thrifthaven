from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Item, Notification

@receiver(post_save, sender=Item)
def notify_admin_on_item_creation(sender, instance, created, **kwargs):
    if created:
        for admin in User.objects.filter(is_staff=True):
            Notification.objects.create(
                user=admin,
                item=instance,
                type="INFO",
                message=f"🆕 New item submitted: '{instance.name}' for ${instance.price}"
            )
