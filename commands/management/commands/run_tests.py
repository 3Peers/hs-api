from django.core.management.base import BaseCommand
import os
import sys


class Command(BaseCommand):
    help = 'Runs tests'

    def handle(self, *args, **kwargs):
        exit_status_code = os.system('PY_ENV=test PIPENV_DONT_LOAD_ENV=1 pipenv run '
                                     './manage.py test -v 2 --noinput')

        if os.WEXITSTATUS(exit_status_code) != 0:
            sys.exit(1)
