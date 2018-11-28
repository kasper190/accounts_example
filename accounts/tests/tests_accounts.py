from accounts.models import (
    Token,
    User,
)
from accounts.serializers import (
    AdminUserListCreateSerializer,
    AdminUserRetrieveUpdateSerializer,
    UserRetrieveUpdateSerializer,
)
from .conftest import (
    _DEFAULT_PASSWORD,
    _USER,
    _USER_ADMIN,
    _USER_NEW,
)
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
import pytest
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_401_UNAUTHORIZED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)
from rest_framework.test import APITestCase
from .tests_factories import UserFactory


@pytest.mark.usefixtures('fixture_user')
class TestsUserAnonymous(APITestCase):
    """
    Tests for anonymous user.
    """
    def test_accounts_unauthorized(self):
        new_user_obj = UserFactory()
        response = self.client.put('/api/accounts/user/password-change/')
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)
        response = self.client.put('/api/accounts/users/%s/' % new_user_obj.id)
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

    def test_user_login(self):
        """ test POST: /api/accounts/login/ """
        data = {
            'email': _USER['email'],
            'password': _DEFAULT_PASSWORD,
        }
        response = self.client.post('/api/accounts/login/', data=data)
        user_obj = User.objects.get(email=_USER['email'])
        token, created = Token.objects.get_or_create(user=user_obj)
        self.assertEqual(response.data['token'], token.key)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_user_login_invalid_password(self):
        """ test POST: /api/accounts/login/ - Invalid password."""
        invalid_password = _DEFAULT_PASSWORD + "InvalidPassword"
        data = {
            'email': _USER['email'],
            'password': invalid_password,
        }
        response = self.client.post('/api/accounts/login/', data=data)
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

    def test_user_logout_anonymous(self):
        """ test POST: /api/accounts/logout/ """
        response = self.client.post('/api/accounts/logout/')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_user_password_reset(self):
        """ test POST: /api/accounts/user/password-reset/ """
        data = {
            'email': _USER['email'],
        }
        response = self.client.post('/api/accounts/user/password-reset/', data=data)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_user_password_reset_token(self):
        """ test PUT: /api/accounts/user/password-reset/<uid>/<token>/ """
        user_obj = User.objects.get(email=_USER['email'])
        uid = urlsafe_base64_encode(force_bytes(user_obj.id)).decode("utf-8")
        token = PasswordResetTokenGenerator().make_token(user_obj)

        new_password = "UserNewPassword#123"
        self.assertEqual(user_obj.check_password(new_password), False)

        data = {
            "password_new": new_password,
            "password_new_confirm": new_password,
        }
        response = self.client.put('/api/accounts/user/password-reset/%s/%s/' % (uid, token), data=data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        user_obj = User.objects.get(email=_USER['email'])
        self.assertEqual(user_obj.check_password(new_password), True)

    def test_user_register(self):
        """ test POST: /api/accounts/register/ """
        data = {
            "first_name": _USER_NEW['first_name'],
            "last_name": _USER_NEW['last_name'],
            "phone_number": _USER_NEW['phone_number'],
            "email": _USER_NEW['email'],
            "password": _DEFAULT_PASSWORD,
            "password_confirm": _DEFAULT_PASSWORD,
        }
        response = self.client.post('/api/accounts/register/', data=data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        user_obj = User.objects.get(email=_USER_NEW['email'])
        self.assertNotEqual(user_obj, None)
        self.assertEqual(user_obj.is_active, False)

    def test_user_register_required_fields(self):
        """ test POST: /api/accounts/register/ - Required fields."""
        data = {
            "first_name": "",
            "last_name": "",
            "phone_number": "",
            "email": "",
            "password": "",
            "password_confirm": "",
        }
        response = self.client.post('/api/accounts/register/', data=data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual({"first_name", "last_name", "email", "password", "password_confirm"}, response.data.keys())

    def test_user_register_invalid_email_format(self):
        """ test POST: /api/accounts/register/ - Invalid email format."""
        invalid_email = "example"
        data = {
            "first_name": _USER_NEW['first_name'],
            "last_name": _USER_NEW['last_name'],
            "phone_number": _USER_NEW['phone_number'],
            "email": invalid_email,
            "password": _DEFAULT_PASSWORD,
            "password_confirm": _DEFAULT_PASSWORD,
        }
        response = self.client.post('/api/accounts/register/', data=data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data.keys())

    def test_user_register_invalid_phone_number_format(self):
        """ test POST: /api/accounts/register/ - Invalid phone number format."""
        invalid_phone_number = "123456"
        data = {
            "first_name": _USER_NEW['first_name'],
            "last_name": _USER_NEW['last_name'],
            "phone_number": invalid_phone_number,
            "email": _USER_NEW['email'],
            "password": _DEFAULT_PASSWORD,
            "password_confirm": _DEFAULT_PASSWORD,
        }
        response = self.client.post('/api/accounts/register/', data=data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn('phone_number', response.data.keys())


@pytest.mark.usefixtures('fixture_user')
class TestsUserDefault(APITestCase):
    """
    Tests for regular user.
    """
    def setUp(self):
        self.user_obj = User.objects.get(email=_USER['email'])
        token, created = Token.objects.get_or_create(user=self.user_obj)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_user_logout(self):
        """ test POST: /api/accounts/logout/ """
        response = self.client.post('/api/accounts/logout/')
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_password_change(self):
        """ test PUT: /api/accounts/user/password-change/ """
        new_password = "UserNewPassword#123"
        data = {
            "password": _DEFAULT_PASSWORD,
            "password_new": new_password,
            "password_new_confirm": new_password,
        }
        response = self.client.put('/api/accounts/user/password-change/', data=data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        user_obj = User.objects.get(email=_USER['email'])
        self.assertEqual(user_obj.check_password(new_password), True)

    def test_password_change_required_fields(self):
        """ test PUT: /api/accounts/user/password-change/ - Required fields."""
        data = {
            "password": "",
            "password_new": "",
            "password_new_confirm": "",
        }
        response = self.client.put('/api/accounts/user/password-change/', data=data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(data.keys(), response.data.keys())

    def test_password_change_invalid_password(self):
        """ test PUT: /api/accounts/user/password-change/ - Invalid password."""
        new_password = "UserNewPassword#123"
        invalid_password = _DEFAULT_PASSWORD + "InvalidPassword"
        data = {
            "password": invalid_password,
            "password_new": new_password,
            "password_new_confirm": new_password,
        }
        response = self.client.put('/api/accounts/user/password-change/', data=data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data.keys())

    def test_password_change_passwords_not_match(self):
        """ test PUT: /api/accounts/user/password-change/ - Passwords do not match."""
        new_password = "UserNewPassword#123"
        data = {
            "password": _DEFAULT_PASSWORD,
            "password_new": new_password,
            "password_new_confirm": new_password + "NotMatch",
        }
        response = self.client.put('/api/accounts/user/password-change/', data=data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn('password_new_confirm', response.data.keys())

    def test_get_all_users_by_user(self):
        """ test GET: /api/accounts/users/ """
        response = self.client.get('/api/accounts/users/')
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_get_user_by_user(self):
        """ test GET: /api/accounts/users/<user_id>/ """
        serializer = UserRetrieveUpdateSerializer(self.user_obj, many=False)
        response = self.client.get('/api/accounts/users/%s/' % self.user_obj.id)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_user_by_user(self):
        """ test POST: /api/accounts/users/ """
        data = {
            "first_name": _USER_NEW['first_name'],
            "last_name": _USER_NEW['last_name'],
            "phone_number": _USER_NEW['phone_number'],
            "email": _USER_NEW['email'],
            "password": _DEFAULT_PASSWORD,
            "password_confirm": _DEFAULT_PASSWORD,
        }
        response = self.client.post('/api/accounts/users/', data=data)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_update_user_by_user(self):
        """ test PUT: /api/accounts/users/<user_id>/ """
        data = {
            "email": _USER_NEW['email'],
            "email_confirm": _USER_NEW['email'],
            "first_name": _USER_NEW['first_name'],
            "last_name": _USER_NEW['last_name'],
            "phone_number": _USER_NEW['phone_number'],
        }
        response = self.client.put('/api/accounts/users/%s/' % self.user_obj.id, data=data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        user_obj = User.objects.get(email=_USER_NEW['email'])
        self.assertEqual(user_obj.first_name, _USER_NEW['first_name'])

    def test_update_user_by_another_user(self):
        """ test PUT: /api/accounts/users/<user_id>/ """
        user_obj = UserFactory()
        data = {
            "first_name": _USER_NEW['first_name'],
        }
        response = self.client.put('/api/accounts/users/%s/' % user_obj.id, data=data)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)


@pytest.mark.usefixtures('fixture_user_admin')
@pytest.mark.usefixtures('fixture_user')
class TestsUserAdmin(APITestCase):
    """
    Tests for admin user.
    """
    def setUp(self):
        self.admin_obj = User.objects.get(email=_USER_ADMIN['email'])
        token, created = Token.objects.get_or_create(user=self.admin_obj)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.user_obj = User.objects.get(email=_USER['email'])

    def test_get_all_users_by_admin(self):
        """ test GET: /api/accounts/users/ """
        users_obj = User.objects.all()
        serializer = AdminUserListCreateSerializer(users_obj, many=True)
        response = self.client.get('/api/accounts/users/')
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_user_by_admin(self):
        """ test GET: /api/accounts/users/<user_id>/ """
        serializer = AdminUserRetrieveUpdateSerializer(self.user_obj, many=False)
        response = self.client.get('/api/accounts/users/%s/' % self.user_obj.id)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_user_by_admin_not_found(self):
        """ test GET: /api/accounts/users/<user_id>/ """
        response = self.client.get('/api/accounts/users/not_found/')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_get_admin_by_user(self):
        """ test GET: /api/accounts/users/<user_id>/ """
        self.client.force_authenticate(user=self.user_obj)
        response = self.client.get('/api/accounts/users/%s/' % self.admin_obj.id)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_create_user_by_admin(self):
        """ test POST: /api/accounts/users/ """
        data = {
            "first_name": _USER_NEW['first_name'],
            "last_name": _USER_NEW['last_name'],
            "phone_number": _USER_NEW['phone_number'],
            "email": _USER_NEW['email'],
            "password": _DEFAULT_PASSWORD,
            "password_confirm": _DEFAULT_PASSWORD,
            "is_active": True,
        }
        response = self.client.post('/api/accounts/users/', data=data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        user_obj = User.objects.get(email=_USER_NEW['email'])
        self.assertNotEqual(user_obj, None)
        self.assertEqual(user_obj.is_active, True)

    def test_create_user_by_admin_invalid_email_format(self):
        """ test POST: /api/accounts/users/ - Invalid email format."""
        invalid_email = "example"
        data = {
            "first_name": _USER_NEW['first_name'],
            "last_name": _USER_NEW['last_name'],
            "phone_number": _USER_NEW['phone_number'],
            "email": invalid_email,
            "password": _DEFAULT_PASSWORD,
            "password_confirm": _DEFAULT_PASSWORD,
            "is_active": True,
        }
        response = self.client.post('/api/accounts/users/', data=data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data.keys())

    def test_create_user_by_admin_invalid_phone_number_format(self):
        """ test POST: /api/accounts/users/ - Invalid phone number format."""
        invalid_phone_number = "123456"
        data = {
            "first_name": _USER_NEW['first_name'],
            "last_name": _USER_NEW['last_name'],
            "phone_number": invalid_phone_number,
            "email": _USER_NEW['email'],
            "password": _DEFAULT_PASSWORD,
            "password_confirm": _DEFAULT_PASSWORD,
            "is_active": True,
        }
        response = self.client.post('/api/accounts/users/', data=data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn('phone_number', response.data.keys())

    def test_update_user_by_admin(self):
        """ test PUT: /api/accounts/users/<user_id>/ """
        data = {
            "email": _USER_NEW['email'],
            "email_confirm": _USER_NEW['email'],
            "first_name": _USER_NEW['first_name'],
            "last_name": _USER_NEW['last_name'],
            "phone_number": _USER_NEW['phone_number'],
            "is_active": True,
        }
        response = self.client.put('/api/accounts/users/%s/' % self.user_obj.id, data=data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        user_obj = User.objects.get(email=_USER_NEW['email'])
        self.assertNotEqual(user_obj, None)
        self.assertEqual(user_obj.first_name, _USER_NEW['first_name'])
