
DEFAULT_APPS = [
    # django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd party apps
    'rest_framework',
    'drf_yasg',
    'rest_framework_simplejwt',
    "rest_framework_simplejwt.token_blacklist",
]

_CUSTOMER_INSTALLED_APPS = DEFAULT_APPS + [
    # project apps
    'accounts',
    'tasks',
    'helpers',
]

_INSTALLED_APPS = _CUSTOMER_INSTALLED_APPS +  [
    'tenant',
]

_INSTALLED_APPS = list(set(_INSTALLED_APPS))   # to remove duplicated app name during 
                                               # adding (+) variables!

