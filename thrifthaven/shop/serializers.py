from rest_framework import serializers
from .models import Category, Item, Notification

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ItemSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True
    )
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'price', 'image', 'video', 'categories', 'user', 'approved', 'stock', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    item = serializers.ReadOnlyField(source='item.name')

    class Meta:
        model = Notification
        fields = ['id', 'user', 'item', 'message', 'is_read', 'created_at']
