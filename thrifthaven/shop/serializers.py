from rest_framework import serializers
from .models import Category, Item, Notification

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class ItemSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)
    image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True)

    class Meta:
        model = Item
        fields = [
            "id","name","description","price","purchase_date",
            "image","video","image_url","video_url",
            "categories","user","approved","stock","offer_price","created_at"
        ]
        read_only_fields = ["user","approved","stock","offer_price","created_at","image_url","video_url"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if obj.image and request else (obj.image.url if obj.image else None)

    def get_video_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.video.url) if obj.video and request else (obj.video.url if obj.video else None)

class NotificationSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    class Meta:
        model = Notification
        fields = ["id","type","message","item","item_name","offer_price","is_read","created_at"]
