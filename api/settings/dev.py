import logging

from .prod import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# optional setting to configure logs to print on stdout
for logger_name, logger_dict in LOGGING['loggers'].items():
    logger_dict['handlers'] = ['console']
logging.config.dictConfig(LOGGING)

# hack to disable autoreload logger
l = logging.getLogger('django.utils.autoreload')
l.disabled = True
