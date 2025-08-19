from rest_framework import serializers
from .models import Category, Item


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class ItemSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, write_only=True, source="categories"
    )

    class Meta:
        model = Item
        fields = ["id", "name", "price", "image", "video", "categories", "category_ids", "user", "approved"]
        read_only_fields = ["user", "approved"]
