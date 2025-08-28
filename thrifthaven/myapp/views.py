from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from .models import Profile
from django.contrib.auth.models import User

# ----------------- SIGNUP -----------------
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------- SIGNIN -----------------
@api_view(['POST'])
@permission_classes([AllowAny])
def signin(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user_obj = User.objects.get(email=email)
        user = authenticate(username=user_obj.username, password=password)
    except User.DoesNotExist:
        user = None

    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Login successful",
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status=status.HTTP_200_OK)

    return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)


# ----------------- PROFILE -----------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "phone": profile.phone,
        "location": profile.location,
        "profile_picture": request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None
    })


# ----------------- UPDATE PROFILE -----------------
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_profile(request):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    # Update username
    username = request.data.get('username')
    if username and username != user.username:
        if User.objects.filter(username=username).exclude(pk=user.pk).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        user.username = username
        user.save()

    # Update phone
    phone = request.data.get('phone')
    if phone:
        profile.phone = phone

    # Update location
    location = request.data.get('location')
    if location:
        profile.location = location

    # Update profile picture
    if 'profile_picture' in request.FILES:
        profile.profile_picture = request.FILES['profile_picture']

    profile.save()

    return Response({
        "message": "Profile updated successfully",
        "username": user.username,
        "phone": profile.phone,
        "location": profile.location,
        "profile_picture": request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None
    }, status=status.HTTP_200_OK)
