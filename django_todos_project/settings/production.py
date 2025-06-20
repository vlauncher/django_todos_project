from .base import *
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_PORT = 465
EMAIL_HOST_USER = 'v2django@gmail.com'
EMAIL_HOST_PASSWORD = 'jmotxzuqgqxlkmlj'
