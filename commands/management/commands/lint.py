from django.core.management.base import BaseCommand
import os
import sys


class Command(BaseCommand):
    help = 'Checks for PEP8 compliance using flake8'

    def handle(self, *args, **kwargs):
        exit_status_code = os.system('PY_ENV=test PIPENV_DONT_LOAD_ENV=1 '
                                     'pipenv run flake8 . --exclude test.py,'
                                     'dev.py,manage.py,__pycache__,__init__.py,'
                                     'migrations --max-line-length=100')

        if os.WEXITSTATUS(exit_status_code) != 0:
            sys.exit(1)
