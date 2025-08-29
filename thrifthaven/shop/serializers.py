from rest_framework import serializers
from .models import Category, Item, Notification

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ItemSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Item
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "item", "item_name", "message", "is_read", "created_at"]
