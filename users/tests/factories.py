import factory
from django.contrib.auth import get_user_model
import pyotp

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    is_active = True
    mfa_enabled = False
    mfa_secret = None

    @factory.post_generation
    def setup_mfa(obj, create, extracted, **kwargs):
        if extracted:  # If mfa_enabled is passed as True
            obj.mfa_secret = pyotp.random_base32()
            obj.mfa_enabled = True
            obj.save()