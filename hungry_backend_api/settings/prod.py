import os
from .common import *
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['hungry-backend-api-prod.herokuapp.com']

DATABASES = {
    'default': dj_database_url.config()
}


REDIS_URL = os.environ['REDIS_URL']
CELERY_BROKER_URL = REDIS_URL