from django.core.management.base import BaseCommand
import os
import sys


class Command(BaseCommand):
    help = 'Runs coverage'

    def handle(self, *args, **kwargs):
        cover_packages = ','.join([
            'apps.user',
            'apps.entities',
            'apps.assessments',
            'apps.problems',
            'apps.globals'
        ])

        exit_status_code = os.system(f'PY_ENV=test PIPENV_DONT_LOAD_ENV=1 \
                                      pipenv run ./manage.py test -v 2 --noinput \
                                      --with-coverage \
                                      --cover-package=\'{cover_packages}\' \
                                      --cover-branches \
                                      --cover-inclusive \
                                      --cover-erase')

        if os.WEXITSTATUS(exit_status_code) != 0:
            sys.exit(1)
