from django.contrib import admin
from .models import Category, Item, Notification

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "display_categories", "price", "approved", "stock", "user", "has_video")

    def display_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    display_categories.short_description = "Categories"

    def has_video(self, obj):
        return bool(obj.video)
    has_video.boolean = True
    has_video.short_description = "Video"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "item", "message", "is_read", "created_at")
