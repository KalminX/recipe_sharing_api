from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import CustomUser
from .models import Recipe, Rating, Comment, Follow, Notification, RecipeShare

class APITests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.recipe = Recipe.objects.create(
            user=self.user,
            title='Test Recipe',
            description='Test Description',
            ingredients='Test Ingredients',
            instructions='Test Instructions',
            prep_time=30,
            cook_time=20,
            servings=4,
            meal_type='dinner',
            is_public=True
        )

    def test_get_profile(self):
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_update_profile(self):
        url = reverse('profile')
        data = {'username': 'updateduser'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')

    # Recipe Management Tests
    def test_create_recipe(self):
        url = reverse('recipe-list')
        data = {
            'title': 'New Recipe',
            'description': 'New Desc',
            'ingredients': 'New Ing',
            'instructions': 'New Inst',
            'prep_time': 20,
            'cook_time': 15,
            'servings': 2,
            'meal_type': 'lunch',
            'is_public': True
        }
        print("This is the url: ", url, "\n")
        response = self.client.post(url, data)
        print(f"This is the data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.objects.count(), 2)

    def test_get_recipe(self):
        url = reverse('recipe-detail', args=[self.recipe.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Recipe')

    def test_search_recipes(self):
        url = reverse('recipe-search')
        response = self.client.get(url, {'q': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    # Interaction Features Tests
    def test_rate_recipe(self):
        url = reverse('recipe-rate', args=[self.recipe.id])
        data = {'score': 4, 'feedback': 'Good recipe'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rating.objects.count(), 1)

    def test_comment_recipe(self):
        url = reverse('recipe-comment', args=[self.recipe.id])
        data = {'content': 'Nice recipe!'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)

    def test_save_recipe(self):
        url = reverse('recipe-save', args=[self.recipe.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user.favorites.count(), 1)

    def test_follow_user(self):
        other_user = CustomUser.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        url = reverse('user-follow', args=[other_user.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Follow.objects.count(), 1)

    # Social Features Tests
    def test_share_recipe(self):
        url = reverse('recipe-share', args=[self.recipe.id])
        data = {'share_type': 'email', 'recipient_email': 'friend@example.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RecipeShare.objects.count(), 1)

    def test_get_user_recipes(self):
        url = reverse('user-recipes', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    # Notifications Test
    def test_get_notifications(self):
        Notification.objects.create(
            recipient=self.user,
            sender=self.user,
            notification_type='recipe_update',
            recipe=self.recipe,
            message='Recipe updated'
        )
        url = reverse('notifications')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
