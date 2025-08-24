from django.urls import path
from .views import signup, signin, profile, update_profile
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('signin/', signin, name='signin'),  
    path('profile/', profile, name='profile'),
    path('update_profile/', update_profile, name='update_profile'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
