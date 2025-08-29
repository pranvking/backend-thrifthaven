from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Item, Notification

# Notify admins when a new item is submitted
@receiver(post_save, sender=Item)
def notify_admin_on_item_creation(sender, instance, created, **kwargs):
    if created:
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                item=instance,
                message=f"🆕 New item submitted: '{instance.name}'"
            )

# Notify item owner when admin approves the item
@receiver(post_save, sender=Item)
def notify_user_on_admin_approval(sender, instance, **kwargs):
    if instance.approved:  # only when approved
        Notification.objects.get_or_create(
            user=instance.user,
            item=instance,
            message=f"✅ Your item '{instance.name}' has been approved! Suggested price: ${instance.offer_price}"
        )
