import factory
from waitlist.models import Waitlist

class WaitlistFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Waitlist

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    is_verified = False
