from django.urls import path
from .views import SignupView, LoginView, SignoutView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("signout/", SignoutView.as_view(), name="signout"),
]