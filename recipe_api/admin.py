from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    CuisineType, DietaryPreference, Recipe, Tag, FavoriteRecipe,
    Rating, Comment, Follow, Notification, RecipeShare
)
from users.models import CustomUser as User


# Custom User Admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'email_verified', 'mfa_enabled', 'date_joined')
    list_filter = ('email_verified', 'mfa_enabled', 'is_staff')
    search_fields = ('username', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'bio', 'profile_picture')}),
        ('Security', {'fields': ('mfa_enabled', 'email_verified')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'bio', 'profile_picture'),
        }),
    )
    readonly_fields = ('date_joined', 'last_login')

# CuisineType Admin
@admin.register(CuisineType)
class CuisineTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# DietaryPreference Admin
@admin.register(DietaryPreference)
class DietaryPreferenceAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Recipe Admin
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'meal_type', 'is_public', 'created_at')
    list_filter = ('meal_type', 'is_public', 'cuisine_types', 'dietary_preferences')
    search_fields = ('title', 'description', 'ingredients')
    raw_id_fields = ('user',)  # For better performance with many users
    filter_horizontal = ('cuisine_types', 'dietary_preferences')  # Nice widget for ManyToMany

# Tag Admin
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('recipes',)

# FavoriteRecipe Admin
@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user__username', 'recipe__title')
    raw_id_fields = ('user', 'recipe')

# Rating Admin
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('user__username', 'recipe__title', 'feedback')
    raw_id_fields = ('user', 'recipe')

# Comment Admin
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'recipe__title', 'content')
    raw_id_fields = ('user', 'recipe')

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'

# Follow Admin
@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'following__username')
    raw_id_fields = ('follower', 'following')

# Notification Admin
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'sender__username', 'message')
    raw_id_fields = ('recipient', 'sender', 'recipe')

# RecipeShare Admin
@admin.register(RecipeShare)
class RecipeShareAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'share_type', 'recipient_email', 'shared_at')
    list_filter = ('share_type', 'shared_at')
    search_fields = ('user__username', 'recipe__title', 'recipient_email')
    raw_id_fields = ('user', 'recipe')