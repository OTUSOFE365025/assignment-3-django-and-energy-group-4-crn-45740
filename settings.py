import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY  = 'your-secret-key'
INSTALLED_APPS = [
    'db',]
DATABASES = {
    'default': {
                'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'products.sqlite3'),
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
