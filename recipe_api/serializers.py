# serializers.py
from rest_framework import serializers
from .models import *
from users.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'bio']

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'ingredients', 'instructions',
            'prep_time', 'cook_time', 'servings', 'created_at', 'updated_at',
            'photo', 'meal_type', 'cuisine_types', 'dietary_preferences', 'is_public'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['score', 'feedback']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']

class RecipeShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeShare
        fields = ['share_type', 'recipient_email']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['notification_type', 'message', 'created_at', 'is_read']
