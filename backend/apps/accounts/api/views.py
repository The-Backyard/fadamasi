from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .pagination import StandardResultsSetPagination
from .permissions import IsAdmin
from .serializers import (
    AdminRegistrationSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)
from .tasks import send_password_reset_email

User = get_user_model()


class ErrorResponse:
    """Standard error response format."""

    @staticmethod
    def create(status_code, message, errors=None):
        """Create standardized error response."""
        response_data = {
            "status": "error",
            "code": status_code,
            "message": message,
        }

        if errors:
            response_data["errors"] = errors

        return Response(response_data, status=status_code)


class SuccessResponse:
    """Standard success response format."""

    @staticmethod
    def create(status_code, message, data=None):
        """Create standardized success response."""
        response_data = {
            "status": "success",
            "code": status_code,
            "message": message,
        }

        if data:
            response_data["data"] = data

        return Response(response_data, status=status_code)


class UserRegistrationView(generics.CreateAPIView):
    """API endpoint for user registration."""

    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            # Generate token for the new user
            refresh = RefreshToken.for_user(user)

            return SuccessResponse.create(
                status.HTTP_201_CREATED,
                _("User registered successfully"),
                {
                    "user": UserProfileSerializer(user).data,
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                },
            )
        except ValidationError as e:
            return ErrorResponse.create(
                status.HTTP_400_BAD_REQUEST,
                _("Registration failed"),
                e.detail,
            )
        except Exception as e:  # noqa: BLE001
            return ErrorResponse.create(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                _("An unexpected error occurred"),
                {"detail": str(e)},
            )


class AdminRegistrationView(generics.CreateAPIView):
    """API endpoint for admin registration.

    Only existing admins can create new admin accounts.
    """

    serializer_class = AdminRegistrationSerializer
    permission_classes = [IsAdmin]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            return SuccessResponse.create(
                status.HTTP_201_CREATED,
                _("Admin user created successfully"),
                {"user": UserProfileSerializer(user).data},
            )
        except ValidationError as e:
            return ErrorResponse.create(
                status.HTTP_400_BAD_REQUEST,
                _("Admin registration failed"),
                e.detail,
            )
        except Exception as e:  # noqa: BLE001
            return ErrorResponse.create(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                _("An unexpected error occurred"),
                {"detail": str(e)},
            )


class UserLoginView(APIView):
    """API endpoint for user login."""

    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data["user"]

            # Generate tokens
            refresh = RefreshToken.for_user(user)

            return SuccessResponse.create(
                status.HTTP_200_OK,
                _("Login successful"),
                {
                    "user": UserProfileSerializer(user).data,
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                },
            )
        except ValidationError as e:
            return ErrorResponse.create(
                status.HTTP_400_BAD_REQUEST,
                _("Login failed"),
                e.detail,
            )
        except Exception as e:  # noqa: BLE001
            return ErrorResponse.create(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                _("An unexpected error occurred"),
                {"detail": str(e)},
            )


class UserLogoutView(APIView):
    """API endpoint for user logout."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return ErrorResponse.create(
                    status.HTTP_400_BAD_REQUEST,
                    _("Refresh token is required"),
                )
            # Blacklist the JWT refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            return SuccessResponse.create(
                status.HTTP_200_OK,
                _("Logout successful"),
            )
        except Exception as e:  # noqa: BLE001
            return ErrorResponse.create(
                status.HTTP_400_BAD_REQUEST,
                _("Logout failed"),
                {"detail": str(e)},
            )


class PasswordResetRequestView(APIView):
    """API endpoint for requesting a password reset."""

    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data["email"]
            user = User.objects.get(email=email)

            # Generate token and send email only if user exists
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Send email asynchronously using Celery
            send_password_reset_email.delay(
                user_email=email,
                user_id=uid,
                token=token,
            )

            return SuccessResponse.create(
                status.HTTP_200_OK,
                _("Password reset email has been sent."),
            )
        except User.DoesNotExist:
            # Still return success to avoid user enumeration
            return SuccessResponse.create(
                status.HTTP_200_OK,
                _("Password reset email has been sent."),
            )
        except ValidationError as e:
            return ErrorResponse.create(
                status.HTTP_400_BAD_REQUEST,
                _("Password reset request failed"),
                e.detail,
            )
        except Exception as e:  # noqa: BLE001
            return ErrorResponse.create(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                _("An unexpected error occurred"),
                {"detail": str(e)},
            )


class PasswordResetConfirmView(APIView):
    """API endpoint for confirming password reset."""

    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

            try:
                uid = force_str(
                    urlsafe_base64_decode(serializer.validated_data["uidb64"])
                )
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return ErrorResponse.create(
                    status.HTTP_400_BAD_REQUEST,
                    _("Invalid user ID."),
                )

            token = serializer.validated_data["token"]

            if default_token_generator.check_token(user, token):
                user.set_password(serializer.validated_data["new_password"])
                user.save()
                return SuccessResponse.create(
                    status.HTTP_200_OK,
                    _("Password has been reset successfully."),
                )
            return ErrorResponse.create(
                status.HTTP_400_BAD_REQUEST,
                _("Invalid or expired token."),
            )
        except ValidationError as e:
            return ErrorResponse.create(
                status.HTTP_400_BAD_REQUEST,
                _("Password reset confirmation failed"),
                e.detail,
            )
        except Exception as e:  # noqa: BLE001
            return ErrorResponse.create(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                _("An unexpected error occurred"),
                {"detail": str(e)},
            )


class UserListView(generics.ListAPIView):
    """API endpoint for listing all users.

    Only accessible by admin users.
    """

    serializer_class = UserProfileSerializer
    permission_classes = [IsAdmin]
    queryset = User.objects.all().order_by("-date_joined")
    pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        try:
            # This will use the standardized pagination
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            # If no pagination (should not happen if pagination_class is set)
            serializer = self.get_serializer(queryset, many=True)
            return SuccessResponse.create(
                status.HTTP_200_OK,
                _("Users retrieved successfully"),
                {"users": serializer.data},
            )
        except Exception as e:  # noqa: BLE001
            return ErrorResponse.create(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                _("An unexpected error occurred"),
                {"detail": str(e)},
            )


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for retrieving, updating and deleting a user.

    Only accessible by admin users.
    """

    serializer_class = UserProfileSerializer
    permission_classes = [IsAdmin]
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)

            return SuccessResponse.create(
                status.HTTP_200_OK,
                _("User retrieved successfully"),
                {"user": serializer.data},
            )
        except Exception as e:  # noqa: BLE001
            return ErrorResponse.create(
                status.HTTP_404_NOT_FOUND,
                _("User not found"),
                {"detail": str(e)},
            )

    def update(self, request, *args, **kwargs):
        try:
            # Prevent changing role via this endpoint for security
            if "role" in request.data:
                return ErrorResponse.create(
                    status.HTTP_400_BAD_REQUEST,
                    _("Role cannot be changed via this endpoint."),
                )

            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return SuccessResponse.create(
                status.HTTP_200_OK,
                _("User updated successfully"),
                {"user": serializer.data},
            )
        except ValidationError as e:
            return ErrorResponse.create(
                status.HTTP_400_BAD_REQUEST,
                _("User update failed"),
                e.detail,
            )
        except Exception as e:  # noqa: BLE001
            return ErrorResponse.create(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                _("An unexpected error occurred"),
                {"detail": str(e)},
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)

            return SuccessResponse.create(
                status.HTTP_204_NO_CONTENT, _("User deleted successfully")
            )
        except Exception as e:  # noqa: BLE001
            return ErrorResponse.create(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                _("An unexpected error occurred"),
                {"detail": str(e)},
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """API endpoint for retrieving and updating user profile."""

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)

            return SuccessResponse.create(
                status.HTTP_200_OK,
                _("Profile retrieved successfully"),
                {"user": serializer.data},
            )
        except Exception as e:  # noqa: BLE001
            return ErrorResponse.create(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                _("An unexpected error occurred"),
                {"detail": str(e)},
            )

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, "_prefetched_objects_cache", None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}  # noqa: SLF001

            return SuccessResponse.create(
                status.HTTP_200_OK,
                _("Profile updated successfully"),
                {"user": serializer.data},
            )
        except ValidationError as e:
            return ErrorResponse.create(
                status.HTTP_400_BAD_REQUEST,
                _("Profile update failed"),
                e.detail,
            )
        except Exception as e:  # noqa: BLE001
            return ErrorResponse.create(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                _("An unexpected error occurred"),
                {"detail": str(e)},
            )
