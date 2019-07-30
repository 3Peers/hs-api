from .prod import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# optional setting to configure logs to print on stdout
del LOGGING['handlers']['debug_file']
for logger_name, logger_dict in LOGGING['loggers'].items():
    logger_dict['handlers'] = ['console']


CELERY_BROKER_URL = 'amqp://rabbitmq:5672'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
CORS_ORIGIN_ALLOW_ALL = True
