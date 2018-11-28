import factory
import pytest
from .tests_factories import UserFactory


_DEFAULT_PASSWORD = "UserUser#123"


_USER = {
    "email": "user@example.com",
    "password": factory.PostGenerationMethodCall('set_password', _DEFAULT_PASSWORD),
    "first_name": "Mark",
    "last_name": "Anderson",
    "phone_number": "+1555444333",
    "is_active": True,
    "is_admin": False,
    "is_superuser": False,
}


_USER_ADMIN = {
    "email": "admin@example.com",
    "password": factory.PostGenerationMethodCall('set_password', _DEFAULT_PASSWORD),
    "first_name": "Mike",
    "last_name": "Hunter",
    "phone_number": "+19998888777",
    "is_active": True,
    "is_admin": True,
    "is_superuser": False,
}


_USER_INACTIVE = {
    "email": "user_inactive@example.com",
    "password": factory.PostGenerationMethodCall('set_password', _DEFAULT_PASSWORD),
    "first_name": "Lewis",
    "last_name": "Steven",
    "phone_number": "+1555666777",
    "is_active": False,
    "is_admin": False,
    "is_superuser": False,
}


_USER_NEW = {
    "email": "user_new@example.com",
    "password": factory.PostGenerationMethodCall('set_password', _DEFAULT_PASSWORD),
    "first_name": "John",
    "last_name": "Spenser",
    "phone_number": "+1777222333",
    "is_active": False,
    "is_admin": False,
    "is_superuser": False,
}


@pytest.fixture
def fixture_user():
    user_obj = UserFactory(**_USER)
    return user_obj


@pytest.fixture
def fixture_user_inactive():
    user_obj = UserFactory(**_USER_INACTIVE)
    return user_obj


@pytest.fixture
def fixture_user_admin():
    user_obj = UserFactory(**_USER_ADMIN)
    return user_obj
