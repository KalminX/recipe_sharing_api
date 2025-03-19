from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import SignupSerializer, LoginSerializer, SignoutSerializer
from .models import CustomUser
from rest_framework_simplejwt.authentication import JWTAuthentication


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"id": user.id, "email": user.email}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            tokens = serializer.create_tokens(user)
            return Response({
                "refresh": tokens["refresh"],
                "access": tokens["access"],
                "user": {"email": user.email, "mfa_enabled": user.mfa_enabled}
            })
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

class SignoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        # Explicitly check if the user is authenticated
        if not request.user.is_authenticated:
            raise AuthenticationFailed(
                detail="Authentication credentials were not provided.",
                code="authentication_failed"
            )

        serializer = SignoutSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "Successfully signed out"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
