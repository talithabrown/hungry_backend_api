from .common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-u5i8jf)nne(*w9zh4#vc_+to9bm)fmyi!n1_%@sd#wl34rlw!i'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hungry_db',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': 'Band@1014'
    }
}