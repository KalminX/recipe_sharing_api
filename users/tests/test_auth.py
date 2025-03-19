import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.core import mail
from rest_framework_simplejwt.tokens import RefreshToken
import pyotp
from users.models import CustomUser
from .factories import UserFactory

pytestmark = pytest.mark.django_db  # Enable database access
client = APIClient()

# --- Helper Functions ---
def get_totp_code(secret):
    """Generate a valid TOTP code for a given secret."""
    totp = pyotp.TOTP(secret)
    return totp.now()

# --- Signup Tests ---
def test_signup_with_valid_data():
    """Test successful signup with valid data."""
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Testpass123!"
    }
    response = client.post("/api/signup/", payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["email"] == "test@example.com"
    assert "id" in response.data
    user = CustomUser.objects.get(email="test@example.com")
    assert user.is_active is False  # Requires verification
    assert user.check_password("Testpass123!")

def test_signup_with_duplicate_email():
    """Test signup fails with duplicate email."""
    UserFactory(email="test@example.com")
    payload = {
        "username": "newuser",
        "email": "test@example.com",
        "password": "Testpass123!"
    }
    response = client.post("/api/signup/", payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data
    assert CustomUser.objects.filter(email="test@example.com").count() == 1

def test_signup_with_missing_fields():
    """Test signup fails with missing required fields."""
    payload = {"username": "testuser"}  # Missing email and password
    response = client.post("/api/signup/", payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data
    assert "password" in response.data

# --- Login Tests ---
def test_login_with_valid_credentials():
    """Test successful login without MFA."""
    user = UserFactory(email="test@example.com")
    print(user)
    payload = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    response = client.post("/api/login/", payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data
    assert response.data["user"]["email"] == "test@example.com"
    assert response.data["user"]["mfa_enabled"] is False

def test_login_with_mfa_enabled_valid_code():
    """Test successful login with MFA enabled and valid code."""
    user = UserFactory(email="test@example.com", setup_mfa=True)
    totp_code = get_totp_code(user.mfa_secret)
    payload = {
        "email": "test@example.com",
        "password": "testpass123",
        "mfa_code": totp_code
    }
    response = client.post("/api/login/", payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data
    assert response.data["user"]["mfa_enabled"] is True

def test_login_with_mfa_enabled_missing_code():
    """Test login fails with MFA enabled but no code provided."""
    user = UserFactory(email="test@example.com", setup_mfa=True)
    payload = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    response = client.post("/api/login/", payload, format="json")
    
    print(f"The response data is: {response.data}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "mfa_code" in response.data

def test_login_with_mfa_enabled_invalid_code():
    """Test login fails with MFA enabled and invalid code."""
    user = UserFactory(email="test@example.com", setup_mfa=True)
    payload = {
        "email": "test@example.com",
        "password": "testpass123",
        "mfa_code": "000000"  # Invalid code
    }
    response = client.post("/api/login/", payload, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "mfa_code" in response.data

def test_login_with_wrong_password():
    """Test login fails with incorrect password."""
    user = UserFactory(email="test@example.com")
    payload = {
        "email": "test@example.com",
        "password": "wrongpass"
    }
    response = client.post("/api/login/", payload, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_login_with_unverified_account():
    """Test login fails if account is not verified."""
    user = UserFactory(email="test1@example.com", is_active=False)
    payload = {
        "email": "test1@example.com",
        "password": "testpass123"
    }
    response = client.post("/api/login/", payload, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    print("This is the response data: ", response.data)
    assert "Account not verified" in response.data["non_field_errors"][0]

# --- Signout Tests ---
def test_signout_with_valid_tokens():
    """Test successful signout with valid refresh token."""
    user = UserFactory(email="test@example.com")
    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    payload = {"refresh": str(refresh)}
    response = client.post("/api/signout/", payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Successfully signed out"
    
    # Verify token is blacklisted by attempting to refresh
    refresh_payload = {"refresh": str(refresh)}
    refresh_response = client.post("/api/token/refresh/", refresh_payload, format="json")
    assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Token is blacklisted" in refresh_response.data["detail"]

def test_signout_without_authentication():
    """Test signout fails without access token."""
    user = UserFactory()
    client.credentials()  # Explicitly clear any credentials
    payload = {"refresh": "hi77uy89"}
    response = client.post("/api/signout/", payload, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_signout_with_invalid_refresh_token():
    """Test signout fails with invalid refresh token."""
    user = UserFactory()
    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    payload = {"refresh": "invalid_token"}
    response = client.post("/api/signout/", payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "refresh" in response.data
    assert "Invalid or expired refresh token" in response.data["refresh"][0]


# --- Token Usage Test ---
def test_protected_endpoint_with_valid_access_token():
    """Test access token works for a protected endpoint."""
    user = UserFactory()
    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    response = client.post("/api/signout/", {"refresh": str(refresh)}, format="json")

    assert response.status_code == status.HTTP_200_OK
