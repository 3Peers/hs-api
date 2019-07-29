from .prod import (
    BASE_DIR,
    SECRET_KEY,
    TEST_RUNNER,
    CORS_ORIGIN_WHITELIST,
    INSTALLED_APPS,
    AUTH_USER_MODEL,
    MIDDLEWARE,
    ROOT_URLCONF,
    TEMPLATES,
    WSGI_APPLICATION,
    DATABASES,
    AUTH_PASSWORD_VALIDATORS,
    REST_FRAMEWORK,
    OAUTH2_PROVIDER,
    OAUTH2_PROVIDER_APPLICATION_MODEL,
    AUTHENTICATION_BACKENDS,
    SOCIAL_AUTH_FACEBOOK_KEY,
    SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS,
    SOCIAL_AUTH_FACEBOOK_SCOPE,
    SOCIAL_AUTH_FACEBOOK_SECRET,
    SOCIAL_AUTH_GITHUB_KEY,
    SOCIAL_AUTH_GITHUB_SCOPE,
    SOCIAL_AUTH_GITHUB_SECRET,
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
    EMAIL_BACKEND,
    EMAIL_HOST,
    EMAIL_HOST_PASSWORD,
    EMAIL_HOST_USER,
    EMAIL_PORT,
    EMAIL_USE_TLS,
    CELERY_BROKER_URL,
    CELERY_IMPORTS,
    LANGUAGE_CODE,
    TIME_ZONE,
    USE_I18N,
    USE_I18N,
    USE_TZ,
    STATIC_URL
)

DEBUG = True
ALLOWED_HOSTS = ['*']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d ' +
            '%(thread)d %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'basic': {
            'format': '[%(levelname)s] %(name)s: %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'filters': ['require_debug_true'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

CELERY_BROKER_URL = 'amqp://localhost'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
CORS_ORIGIN_ALLOW_ALL = True
