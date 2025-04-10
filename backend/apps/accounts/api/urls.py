from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    AdminRegistrationView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    UserDetailView,
    UserListView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    UserRegistrationView,
)

app_name = "accounts"

api_v1_patterns = [
    # Authentication endpoints
    path(
        "token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "token/verify/",
        TokenVerifyView.as_view(),
        name="token_verify",
    ),
    path(
        "register/",
        UserRegistrationView.as_view(),
        name="register",
    ),
    path(
        "login/",
        UserLoginView.as_view(),
        name="login",
    ),
    path(
        "logout/",
        UserLogoutView.as_view(),
        name="logout",
    ),
    path(
        "password-reset/",
        PasswordResetRequestView.as_view(),
        name="password_reset",
    ),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # User profile endpoint
    path(
        "profile/",
        UserProfileView.as_view(),
        name="profile",
    ),
    # Admin endpoints
    path(
        "admin/register/",
        AdminRegistrationView.as_view(),
        name="admin_register",
    ),
    path(
        "admin/users/",
        UserListView.as_view(),
        name="user_list",
    ),
    path(
        "admin/users/<uuid:pk>/",
        UserDetailView.as_view(),
        name="user_detail",
    ),
]

urlpatterns = [
    path(
        "v1/auth/",
        include((api_v1_patterns, app_name), namespace="v1"),
    ),
]
