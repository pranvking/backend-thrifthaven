from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Category, Item
from .serializers import CategorySerializer, ItemSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()   # 👈 add this line
    serializer_class = CategorySerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()       # 👈 add this line
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.action == "list":
            return Item.objects.filter(approved=True)  # only approved visible
        return Item.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, approved=False)
