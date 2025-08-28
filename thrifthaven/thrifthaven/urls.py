from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('myapp.urls')),   # Auth and profile
    path('api/', include('shop.urls')),
    path('api/', include('myapp.urls')),# Shop endpoints
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
