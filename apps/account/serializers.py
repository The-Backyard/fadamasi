from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Profile, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        """Meta class to define the model and fields for the serializer."""

        model = User
        fields = ["id", "username", "email"]


class TokenObtainPairSerializerWithUser(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["email"] = user.email
        token["bio"] = user.profile.bio
        token["picture"] = str(user.profile.picture)
        return token


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        """Meta class to define the model and fields for the serializer."""

        model = User
        fields = ["username", "email", "password", "password2"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        """Meta class to define the model and fields for the serializer."""

        model = Profile
        fields = ["bio", "picture", "phone_number", "address"]
        extra_kwargs = {
            "bio": {"required": False},
            "picture": {"required": False},
            "phone_number": {"required": False},
            "address": {"required": False},
        }
