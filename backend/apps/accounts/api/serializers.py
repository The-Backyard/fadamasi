from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from .validators import PhoneNumberValidator, UsernameValidator

User = get_user_model()


class BaseUserRegistrationSerializer(serializers.ModelSerializer):
    """Base serializer for user registration."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        validators=[validate_password],
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )
    username = serializers.CharField(
        validators=[UsernameValidator()],
    )
    phone_number = serializers.CharField(
        required=False,
        allow_blank=True,
        validators=[PhoneNumberValidator()],
    )

    class Meta:
        """Meta options for the serializer class."""

        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "phone_number",
        ]

    def validate_email(self, value):
        """Validate email format and uniqueness."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                _("A user with this email already exists.")
            )
        return value.lower()

    def validate_username(self, value):
        """Validate username uniqueness."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                _("A user with this username already exists.")
            )
        return value

    def validate(self, attrs):
        """Validate password matching."""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": _("Password fields didn't match.")}
            )
        return attrs


class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    """Serializer for customer user registration."""

    def create(self, validated_data):
        """Create a new customer user."""
        validated_data.pop("password_confirm")
        # Set role explicitly to customer
        validated_data["role"] = User.CUSTOMER
        return User.objects.create_user(**validated_data)


class AdminRegistrationSerializer(BaseUserRegistrationSerializer):
    """Serializer for admin user registration."""

    def create(self, validated_data):
        """Create a new admin user."""
        validated_data.pop("password_confirm")
        # Set role explicitly to admin
        validated_data["role"] = User.ADMIN
        # Set is_staff to True as well to allow Django admin access
        validated_data["is_staff"] = True
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        """Validate login credentials."""
        email = attrs.get("email", "").lower()
        password = attrs.get("password", "")

        if not email or not password:
            raise serializers.ValidationError(
                {"error": _('Must include "email" and "password".')}
            )

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )

        if not user:
            raise AuthenticationFailed(
                {"error": _("Unable to log in with provided credentials.")}
            )

        if not user.is_active:
            raise AuthenticationFailed({"error": _("User account is disabled.")})

        attrs["user"] = user
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Validate email exists in the system."""
        email = value.lower()
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                _("No user found with this email address.")
            )
        return email


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""

    token = serializers.CharField(required=True)
    uidb64 = serializers.CharField(required=True)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        validators=[validate_password],
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        """Validate passwords match."""
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": _("Password fields didn't match.")}
            )
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""

    full_name = serializers.CharField(read_only=True)
    phone_number = serializers.CharField(
        required=False,
        allow_blank=True,
        validators=[PhoneNumberValidator()],
    )

    class Meta:
        """Meta options for the user profile serializer class."""

        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone_number",
            "role",
            "date_joined",
            "is_active",
        ]
        read_only_fields = [
            "id",
            "username",
            "email",
            "role",
            "date_joined",
            "is_active",
        ]
