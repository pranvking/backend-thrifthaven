from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from .models import Category, Item, Notification
from .serializers import CategorySerializer, ItemSerializer, NotificationSerializer

def compute_offer_price(item: Item) -> Decimal:
    """10% per full year since purchase_date (cap 70%), then add 15% on top."""
    base = item.price
    years = 0
    if item.purchase_date:
        years = max(0, date.today().year - item.purchase_date.year - ((date.today().month, date.today().day) < (item.purchase_date.month, item.purchase_date.day)))
    depreciation = min(Decimal(years) * Decimal("0.10"), Decimal("0.70"))
    depreciated = (base * (Decimal("1.00") - depreciation))
    display = (depreciated * Decimal("1.15"))
    return display.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return hasattr(obj, "user") and obj.user == request.user

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.select_related("user").prefetch_related("categories").all().order_by("-created_at")
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def perform_create(self, serializer):
        obj = serializer.save(user=self.request.user)
        return obj

    # Admin sees only items that haven't been processed (no offer yet and not approved)
    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAdminUser])
    def pending(self, request):
        qs = Item.objects.filter(approved=False, offer_price__isnull=True).order_by("created_at")
        return Response(self.get_serializer(qs, many=True).data)

    # Admin: create offer and notify user (do NOT mark approved)
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        try:
            item = self.get_object()
        except:
            raise NotFound("Item not found")
        if item.offer_price:  # already offered
            return Response({"detail":"Offer already sent."}, status=400)
        offer = compute_offer_price(item)
        item.offer_price = offer
        item.save()
        Notification.objects.create(
            user=item.user,
            item=item,
            type="OFFER",
            offer_price=offer,
            message=f"We made an offer for '{item.name}': ${offer}. Accept or decline."
        )
        return Response({"status":"offer_sent","offer_price": str(offer)})

    # Admin: decline => delete item and notify owner
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def decline(self, request, pk=None):
        item = self.get_object()
        Notification.objects.create(
            user=item.user,
            item=None,
            type="DECLINED",
            message=f"Your item '{item.name}' was declined and removed."
        )
        item.delete()
        return Response({"status":"declined_and_deleted"})

    # Owner: accept admin offer => publish listing
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsOwner])
    def accept_offer(self, request, pk=None):
        item = self.get_object()
        if not item.offer_price:
            return Response({"detail":"No offer to accept."}, status=400)
        item.approved = True
        item.save()
        Notification.objects.create(
            user=item.user,
            item=item,
            type="APPROVED",
            message=f"Your item '{item.name}' is now live at ${item.offer_price}."
        )
        return Response({"status":"accepted","approved": True})

    # Owner: decline admin offer => delete item
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsOwner])
    def decline_offer(self, request, pk=None):
        item = self.get_object()
        Notification.objects.create(
            user=item.user,
            item=None,
            type="DECLINED",
            message=f"You declined the offer for '{item.name}'. The item was removed."
        )
        item.delete()
        return Response({"status":"declined_and_deleted_by_owner"})

    # (Optional) mark sold by owner
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsOwner])
    def mark_sold(self, request, pk=None):
        item = self.get_object()
        item.stock = True
        item.save()
        Notification.objects.create(
            user=item.user,
            item=item,
            type="SOLD",
            message=f"'{item.name}' marked as sold."
        )
        return Response({"status":"sold"})

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only the current user's notifications
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        raise PermissionDenied("Notifications are system-generated.")

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        if notif.user != request.user:
            raise PermissionDenied("Not yours.")
        notif.is_read = True
        notif.save()
        return Response({"status":"read"})

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"status":"all_read"})
