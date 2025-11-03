from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .services.hedera_service import create_hedera_account
from utils.encryption import encrypt_value, decrypt_value

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('id','username','wallet_address')

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "password",
            "hedera_account_id", "hedera_public_key", "hedera_private_key"
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data.get("email", "")
        )
        user.set_password(validated_data["password"])

        # Create Hedera account on signup
        hedera_info = create_hedera_account()

        # Encrypt before saving
        user.hedera_account_id = encrypt_value(hedera_info["hedera_account_id"])
        user.hedera_public_key = encrypt_value(hedera_info["hedera_public_key"])
        user.hedera_private_key = encrypt_value(hedera_info["hedera_private_key"])

        user.save()
        return user

    def to_representation(self, instance):
        """Optionally decrypt before returning (useful for admin/internal API)"""
        data = super().to_representation(instance)
        try:
            data["hedera_account_id"] = decrypt_value(instance.hedera_account_id)
            data["hedera_public_key"] = decrypt_value(instance.hedera_public_key)
            data["hedera_private_key"] = decrypt_value(instance.hedera_private_key)
        except Exception:
            # In case of missing encryption key or invalid cipher
            data["hedera_account_id"] = None
            data["hedera_public_key"] = None
            data["hedera_private_key"] = None
        return data


class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "hedera_account_id"]

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            raise AuthenticationFailed('Invalid username or password')

        refresh = RefreshToken.for_user(user)
        attrs['refresh'] = str(refresh)
        attrs['access'] = str(refresh.access_token)
        return attrs