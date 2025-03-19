from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin
from django.urls import path, include
from django.urls import path
from recipe_api.views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="Your App API",
        default_version='v1',
        description="API for user authentication and recipe management with JWT",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('users.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # urls.py


    # User Management
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # Recipe Management
    path('recipes/', RecipeListCreateView.as_view(), name='recipe-list'),
    path('recipes/<int:pk>/', RecipeDetailView.as_view(), name='recipe-detail'),
    path('recipes/search/', RecipeSearchView.as_view(), name='recipe-search'),
    
    # Interaction Features
    path('recipes/<int:pk>/rate/', RecipeRateView.as_view(), name='recipe-rate'),
    path('recipes/<int:pk>/comments/', RecipeCommentView.as_view(), name='recipe-comment'),
    path('recipes/<int:pk>/save/', RecipeSaveView.as_view(), name='recipe-save'),
    path('users/<int:user_id>/follow/', UserFollowView.as_view(), name='user-follow'),
    
    # Social Features
    path('recipes/<int:pk>/share/', RecipeShareView.as_view(), name='recipe-share'),
    path('users/<int:user_id>/recipes/', UserRecipesView.as_view(), name='user-recipes'),
    
    # Notifications
    path('notifications/', NotificationView.as_view(), name='notifications'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

