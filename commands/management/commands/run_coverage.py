from django.core.management.base import BaseCommand
import os
import sys


class Command(BaseCommand):
    help = 'Runs coverage'

    def handle(self, *args, **kwargs):
        if os.getenv('PY_ENV') != 'test':
            sys.exit('Please ensure PY_ENV environment variable is set to \'test\'')
        os.system('pipenv run ./manage.py test -v 2 --noinput\
                      --with-coverage\
                      --cover-package=\'user,entities,assessments,problems\'\
                      --cover-branches\
                      --cover-inclusive\
                      --cover-erase')
