from .base import *
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'