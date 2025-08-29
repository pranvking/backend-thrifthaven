from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction
from .models import Profile

# ------------------ USER SERIALIZER ------------------
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    location = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'phone', 'location']

    def validate(self, data):
        # Check if email already exists
        if User.objects.filter(username=data['email']).exists():
            raise serializers.ValidationError({"email": "User with this email already exists."})

        # Check password match
        if data['password'] != data.get('confirm_password'):
            raise serializers.ValidationError({"password": "Passwords do not match"})

        # Validate phone number
        phone = data.get('phone', '')
        if not phone.isdigit() or len(phone) != 10:
            raise serializers.ValidationError({"phone": "Phone number must be exactly 10 digits."})

        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        phone = validated_data.pop('phone')
        location = validated_data.pop('location', '')

        # Create user with email as username
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        # Create profile linked to the user
        Profile.objects.create(
            user=user,
            phone=phone,
            location=location or None
        )

        return user


# ------------------ PROFILE SERIALIZER ------------------
class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", required=False)
    profile_picture = serializers.SerializerMethodField()
    location = serializers.CharField(required=False)

    class Meta:
        model = Profile
        fields = ['email', 'username', 'phone', 'profile_picture', 'location']

    def get_profile_picture(self, obj):
        request = self.context.get("request")
        if obj.profile_picture:
            return request.build_absolute_uri(obj.profile_picture.url)
        return None

    def update(self, instance, validated_data):
        # Extract nested user data
        user_data = validated_data.pop('user', {})

        # --- Update username if provided ---
        new_username = user_data.get('username', instance.user.username).strip()
        if new_username != instance.user.username:
            if User.objects.filter(username=new_username).exclude(pk=instance.user.pk).exists():
                raise serializers.ValidationError({"username": "This username is already taken."})
            instance.user.username = new_username
            instance.user.save()

        # --- Handle profile picture update explicitly ---
        if "profile_picture" in validated_data:
            profile_picture = validated_data.pop("profile_picture")
            if profile_picture:
                instance.profile_picture = profile_picture
            # If null: keep existing picture

        # --- Update other profile fields ---
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
