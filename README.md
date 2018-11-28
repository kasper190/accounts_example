# accounts - Django REST basic authentication

`accounts` is a set of basic authorization actions for the Django REST framework apps that covers:
- login
- logout
- registration
- account activation
- password change
- password reset
- user detail
- user update
- user list

Requirements:
- [Python] (3.5.x)
- [Django] (1.11.7)
- [Django REST framework] (3.7.7)

To install `accounts` in your project, move the [/accounts] dictionary to the project dictionary and add the following settings variables (from [accounts_settings.py]) to the `settings.py` file.

```python
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
```

## accounts_example installation

To run accounts_example locally, first setup and activate virtual environment for it and then:

__1. Install requirements using pip:__
```shell
pip3 install -r requirements.txt
```

__2. Make migrations:__
```shell
python3 manage.py makemigrations
```

__3. Create the tables in the database by__ `migrate` __command:__
```shell
python3 manage.py migrate
```

__4. Set the settings variables (from [accounts_settings.py]) in the [accounts_example/settings.py] file.__

__5. Create a user who can login to the admin site:__
```shell
python3 manage.py createsuperuser
```

__6. Run the server:__
```shell
python3 manage.py runserver
```

__Now the accounts_example application is ready for use.__


## Tests
Tests are available in the `/accounts/tests/` dictionary. To run tests, run the commmand:
```shell
pytest
```

NOTE: The [Postman] enviroment and collection are available in the [accounts.postman_environment.json] and [accounts.postman_collection.json] files.

[Python]: <https://www.python.org/>
[Django]: <https://www.djangoproject.com/>
[Django REST framework]: <http://www.django-rest-framework.org/>
[/accounts]: <./accounts/>
[accounts_settings.py]: <./accounts_settings.py>
[accounts_example/settings.py]: <./accounts_example/settings.py>
[Postman]: <https://www.getpostman.com/>
[accounts.postman_environment.json]: <./accounts.postman_environment.json>
[accounts.postman_collection.json]: <./accounts.postman_collection.json>

