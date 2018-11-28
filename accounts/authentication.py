from accounts.models import (
    Token,
)
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone
from django.utils.six import text_type
from rest_framework.authentication import (
    get_authorization_header,
    TokenAuthentication,
)
from rest_framework.exceptions import (
    AuthenticationFailed,
    PermissionDenied
)


class ExpiringTokenAuthentication(TokenAuthentication):
    model = Token

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            return None
        elif len(auth) > 2:
            return None

        try:
            token = auth[1].decode()
        except UnicodeError:
            return None

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        model = self.get_model()

        try:
            token = model.objects.select_related('user').get(key=key)
        # except Exception as e:
        #     print(e)
        except model.DoesNotExist:
            raise AuthenticationFailed('Invalid token.')
        if token.logout:
            raise AuthenticationFailed('Invalid token.')
        if not token.user.is_active:
            raise PermissionDenied('User inactive or deleted.')

        if token.updated < timezone.now() - settings.TOKEN_EXPIRATION_TIME:
            raise AuthenticationFailed('Token has expired.')

        token.updated = timezone.now()
        token.save()
        return token.user, token


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (text_type(user.id) + text_type(timestamp)) + text_type(user.is_active)
