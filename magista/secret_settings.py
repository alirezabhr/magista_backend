import enum
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class ProjectMode(enum.Enum):
    Debug = True
    Production = False


mode = ProjectMode.Debug

__debug_db = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'magista',
        'USER': 'postgres',
        'PASSWORD': 'alireza1379',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

__prod_db = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'magista',
        'USER': 'magista_user',
        'PASSWORD': 'M@g!St@_1400',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# -----------------

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-4xaah-z$9v_qyr6&_-st#vjjbdyvh@0m%8d-x(ew-9+4)9n0@='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if mode == ProjectMode.Debug else False

ALLOWED_HOSTS = ['*'] if mode == ProjectMode.Debug else ['.magista.ir', '194.5.205.48']

DATABASES = __debug_db if mode == ProjectMode.Debug else __prod_db

TERMINAL_CODE = 2311496
MERCHANT_CODE = 5059538

SENTRY_DSN = 'https://3a4be8a90d4c4a75b25709d253425f17@sentry.hamravesh.com/280' if mode == ProjectMode.Debug else 'https://38114027f274485985d4365385908afc@sentry.hamravesh.com/252'