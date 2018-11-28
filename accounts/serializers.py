from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from .models import Token
from rest_framework.exceptions import (
    AuthenticationFailed,
    PermissionDenied,
)
from rest_framework.serializers import (
    CharField,
    EmailField,
    ModelSerializer,
    Serializer,
    ValidationError,
)


User = get_user_model()


class UserCreateSerializer(ModelSerializer):
    """
    User create serializer.
    """
    password = CharField(label='Password', write_only=True)
    password_confirm = CharField(label='Password confirm', write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'password',
            'password_confirm',
        )

    def validate_password(self, value):
        try:
            validate_password(value)
        except Exception as e:
            raise ValidationError(list(e.messages))
        return value

    def validate_password_confirm(self, value):
        data = self.get_initial()
        password = data.get('password')
        password_confirm = value
        if password != password_confirm:
            raise ValidationError("Passwords must match.")
        return value

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user_obj = User(**validated_data)
        user_obj.set_password(validated_data['password'])
        user_obj.save()
        return user_obj


class AdminUserListCreateSerializer(UserCreateSerializer):
    """
    User list/create serializer for admin only.
    """
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'date_joined',
            'last_login',
            'updated',
            'is_active',
            'is_admin',
            'is_superuser',
            'password',
            'password_confirm',
        )
        read_only_fields = ['id', 'date_joined', 'last_login', 'updated']


class AdminUserRetrieveUpdateSerializer(ModelSerializer):
    """
    User retrieve/update serializer for admin only.
    """
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'is_active',
            'is_admin',
            'is_superuser',
        )
        extra_kwargs = {
            'email': {
                'required': False
            }
        }
        read_only_fields = ['id']


class UserLoginSerializer(Serializer):
    """
    User login serializer.
    """
    email = EmailField(label='Email')
    password = CharField(label='Password', write_only=True)
    token = CharField(label='Token', allow_blank=True, read_only=True)

    def validate(self, data):
        email = data['email']
        password = data['password']
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            raise PermissionDenied("User with this email does not exists.")
        if not user_obj.check_password(password):
            raise AuthenticationFailed("Incorrect credentials please try again.")
        if user_obj.check_password(password):
            if not user_obj.is_active:
                raise PermissionDenied("User is inactive.")
            user_obj.last_login = timezone.now()
            user_obj.save()

            data['token'] = Token.objects.create(user=user_obj)
            return data
        raise AuthenticationFailed("Invalid credentials.")


class UserPasswordChangeSerializer(Serializer):
    """
    Password changing serializer.
    """
    password = CharField(label='Password', write_only=True)
    password_new = CharField(label='New Password', write_only=True)
    password_new_confirm = CharField(label='Confirm New Password', write_only=True)

    def validate_password(self, value):
        data = self.get_initial()
        user = self.context['request'].user
        password = data.get('password')
        try:
            user_obj = User.objects.get(email=user)
        except User.DoesNotExist:
            raise ValidationError("User with this email does not exist.")
        if not user_obj.check_password(password):
            raise ValidationError("You passed invalid password.")
        return value

    def validate_password_new(self, value):
        try:
            validate_password(value)
        except Exception as e:
            raise ValidationError(list(e.messages))
        return value

    def validate_password_new_confirm(self, value):
        data = self.get_initial()
        password_new = data.get('password_new')
        password_new_confirm = value
        if password_new != password_new_confirm:
            raise ValidationError("Passwords must match.")
        return value


class UserPasswordChangeTokenSerializer(ModelSerializer):
    """
    User password reset link serializer.
    """
    password_new = CharField(label='New Password', write_only=True)
    password_new_confirm = CharField(label='Confirm New Password', write_only=True)

    class Meta:
        model = User
        fields = (
            'password_new',
            'password_new_confirm',
        )

    def validate_password_new(self, value):
        try:
            validate_password(value)
        except Exception as e:
            raise ValidationError(list(e.messages))
        return value

    def validate_password_new_confirm(self, value):
        data = self.get_initial()
        password_new = data.get('password_new')
        password_new_confirm = value
        if password_new != password_new_confirm:
            raise ValidationError("Passwords must match.")
        return value


class UserPasswordResetSerializer(Serializer):
    """
    Password reset serializer.
    """
    email = EmailField(label='E-mail')

    def validate_email(self, value):
        data = self.get_initial()
        email = data.get('email')
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError("User with this email does not exist.")
        return value


class UserRetrieveUpdateSerializer(ModelSerializer):
    """
    User retrieve/update serializer for regular user.
    """
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'phone_number',
        )
        extra_kwargs = {
            'email': {
                'required': False
            }
        }
        read_only_fields = ['id']
