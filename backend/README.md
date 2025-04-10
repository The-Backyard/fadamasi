# API Endpoints

The authentication system provides the following endpoints:

| Endpoint | Method | Description | Authentication Required |
|----------|--------|-------------|------------------------|
| `/api/v1/accounts/register/` | POST | Register a new customer user | No |
| `/api/v1/accounts/login/` | POST | Login user and get authentication tokens | No |
| `/api/v1/accounts/logout/` | POST | Logout user and blacklist refresh token | Yes |
| `/api/v1/accounts/token/` | POST | Obtain JWT token pair | No |
| `/api/v1/accounts/token/refresh/` | POST | Refresh JWT access token | No |
| `/api/v1/accounts/password_reset/` | POST | Request password reset email | No |
| `/api/v1/accounts/password_reset_confirm/` | POST | Confirm password reset with token | No |
| `/api/v1/accounts/profile/` | GET | Retrieve current user profile | Yes |
| `/api/v1/accounts/profile/` | PUT/PATCH | Update current user profile | Yes |
| `/api/v1/accounts/admin/register/` | POST | Register a new admin user | Yes (Admin only) |
| `/api/v1/accounts/admin/users/` | GET | List all users | Yes (Admin only) |
| `/api/v1/accounts/admin/users/{uuid}/` | GET | Retrieve specific user details | Yes (Admin only) |
| `/api/v1/accounts/admin/users/{uuid}/` | PUT/PATCH | Update specific user | Yes (Admin only) |
| `/api/v1/accounts/admin/users/{uuid}/` | DELETE | Delete specific user | Yes (Admin only) |
