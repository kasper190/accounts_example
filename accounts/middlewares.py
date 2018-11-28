from accounts.models import (
    Token,
)
from django.utils import timezone
from rest_framework.authentication import get_authorization_header


def get_token_from_request(request):
    auth = get_authorization_header(request).split()

    if not auth or auth[0].lower() != 'Token'.lower().encode():
        return None

    if len(auth) == 1:
        return None
    elif len(auth) > 2:
        return None

    try:
        token = auth[1].decode()
    except UnicodeError:
        return None

    return token


class TokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        token = get_token_from_request(request)
        if token:
            try:
                token = Token.objects.get(key=token)
                token.updated = timezone.now()
                token.save()
            except Exception as e:
                print(e)
        return None
