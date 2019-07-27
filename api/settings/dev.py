from .prod import *

DEBUG = True

ALLOWED_HOSTS = ['*']

CELERY_BROKER_URL = 'amqp://localhost'
