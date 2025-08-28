from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile
from django.db import transaction

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    location = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'phone', 'location']

    def validate(self, data):
        if User.objects.filter(username=data['email']).exists():
            raise serializers.ValidationError({"email": "User with this email already exists."})
        if data['password'] != data.get('confirm_password'):
            raise serializers.ValidationError({"password": "Passwords do not match"})
        phone = data.get('phone', '')
        if not phone.isdigit() or len(phone) != 10:
            raise serializers.ValidationError({"phone": "Phone number must be exactly 10 digits."})
        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        phone = validated_data.pop('phone')
        location = validated_data.pop('location', '')

        user = User.objects.create_user(
            username=validated_data['email'],  # use email as username
            email=validated_data['email'],
            password=validated_data['password']
        )

        Profile.objects.create(user=user, phone=phone, location=location or None)
        return user


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", required=False)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    location = serializers.CharField(required=False)

    class Meta:
        model = Profile
        fields = ['email', 'username', 'phone', 'profile_picture', 'location']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})

        # Update username if provided
        new_username = user_data.get('username', instance.user.username).strip()
        if new_username != instance.user.username:
            if User.objects.filter(username=new_username).exclude(pk=instance.user.pk).exists():
                raise serializers.ValidationError({"username": "This username is already taken."})
            instance.user.username = new_username
            instance.user.save()

        # Update Profile fields
        for attr, value in validated_data.items():
            if value is not None:
                setattr(instance, attr, value)
        instance.save()
        return instance
