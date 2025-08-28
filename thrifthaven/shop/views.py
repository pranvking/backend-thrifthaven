from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, Item, Notification
from .serializers import CategorySerializer, ItemSerializer, NotificationSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]  # Login required


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Save item without categories first
        item = serializer.save(user=self.request.user)

        # Attach categories from FormData
        categories = self.request.data.getlist('categories')
        if categories:
            item.categories.set(categories)
        item.save()

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        item = self.get_object()
        item.approved = True
        item.stock = True
        item.save()
        return Response({"status": "Item approved and stock updated"})

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def decline(self, request, pk=None):
        item = self.get_object()
        item.delete()
        return Response({"status": "Item declined and deleted"})


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": "Notification marked as read"})
