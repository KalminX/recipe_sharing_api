# views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import *
from .serializers import *

class ProfileView(APIView):
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RecipeListCreateView(generics.ListCreateAPIView):
    queryset = Recipe.objects.filter(is_public=True)
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RecipeDetailView(generics.RetrieveAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

class RecipeSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '')
        recipes = Recipe.objects.filter(
            title__icontains=query, is_public=True
        ) | Recipe.objects.filter(
            description__icontains=query, is_public=True
        )
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data)

class RecipeRateView(APIView):
    def post(self, request, pk):
        recipe = Recipe.objects.get(pk=pk)
        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            Rating.objects.update_or_create(
                user=request.user,
                recipe=recipe,
                defaults=serializer.validated_data
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RecipeCommentView(APIView):
    def post(self, request, pk):
        recipe = Recipe.objects.get(pk=pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RecipeSaveView(APIView):
    def post(self, request, pk):
        recipe = Recipe.objects.get(pk=pk)
        favorite, created = FavoriteRecipe.objects.get_or_create(
            user=request.user,
            recipe=recipe
        )
        return Response(status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class UserFollowView(APIView):
    def post(self, request, user_id):
        following = CustomUser.objects.get(id=user_id)
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=following
        )
        return Response(status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class RecipeShareView(APIView):
    def post(self, request, pk):
        recipe = Recipe.objects.get(pk=pk)
        serializer = RecipeShareSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRecipesView(generics.ListAPIView):
    serializer_class = RecipeSerializer
    
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Recipe.objects.filter(user_id=user_id, is_public=True).order_by('-created_at')

class NotificationView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')