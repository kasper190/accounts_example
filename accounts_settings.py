# imports
import os
from datetime import timedelta
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Django settings
AUTH_USER_MODEL = 'accounts.User'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'accounts.authentication.ExpiringTokenAuthentication',
    ),
}

# accounts settings variables
TOKEN_EXPIRATION_TIME = timedelta(days=1)
PASSWORD_RESET_TIMEOUT_DAYS = 1

EMAIL_HOST = 'smtp.example.com'
EMAIL_HOST_USER = 'example@example.com'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'example@example.com'

UI_URL = 'http://127.0.0.1:8000'
UI_ACCOUNT_ACTIVATE_PATH = '/api/accounts/user/activate/'
BACKEND_URL = 'http://127.0.0.1:8000'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')