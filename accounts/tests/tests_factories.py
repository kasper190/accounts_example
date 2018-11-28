import datetime
import factory
import pytz
from accounts.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ['phone_number']

    password = factory.PostGenerationMethodCall('set_password', 'useruser')
    email = factory.Sequence(lambda n: 'user{}@example.com'.format(n))
    first_name = factory.Sequence(lambda n: 'Firstname{}'.format(n))
    last_name = factory.Sequence(lambda n: 'Lastname{}'.format(n))
    phone_number = None
    updated = datetime.datetime.now(pytz.utc)
    last_login = None
    is_active = True
    is_admin = False
    is_superuser = False
