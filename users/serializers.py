from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser

class SignupSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Creates a new user with a username, email, and password.
    The user is inactive until email verification is completed.
    """
    class Meta:
        model = CustomUser
        fields = ("username", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            is_active=False  # Requires email verification
        )
        # Placeholder for sending email verification (e.g., via Celery)
        return user

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Validates email and password, with optional MFA code if enabled.
    Returns access and refresh tokens on success.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    mfa_code = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Required if MFA is enabled for the user."
    )

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        mfa_code = data.get("mfa_code")

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError({"non_field_errors": ["Invalid credentials"]})
        if not user.is_active:
            print("Account is not verified")
            raise serializers.ValidationError({"non_field_errors": ["Account not verified"]})

        print("Account is verified")
        
        if user.mfa_enabled:
            if not mfa_code:
                raise serializers.ValidationError({"mfa_code": ["MFA code is required"]})
            if not user.verify_mfa_code(mfa_code):
                raise serializers.ValidationError({"mfa_code": ["Invalid MFA code"]})

        data["user"] = user
        return data

    def create_tokens(self, user):
        """Generate JWT access and refresh tokens for the user."""
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

class SignoutSerializer(serializers.Serializer):
    """
    Serializer for user signout.
    Requires a refresh token to blacklist it, effectively logging out the user.
    """
    refresh = serializers.CharField(
        required=True,
        help_text="The refresh token to be blacklisted."
    )

    def validate(self, data):
        refresh_token = data.get("refresh")
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token
        except Exception as e:
            raise serializers.ValidationError({"refresh": ["Invalid or expired refresh token"]})
        return data
