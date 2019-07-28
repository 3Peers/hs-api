from .prod import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# optional setting to configure logs to print on stdout
for logger_name, logger_dict in LOGGING['loggers'].items():
    logger_dict['handlers'] = ['console']

CELERY_BROKER_URL = 'amqp://localhost'

CORS_ORIGIN_ALLOW_ALL = True
