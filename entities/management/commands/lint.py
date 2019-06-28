from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    help = 'Checks for PEP8 compliance using flake8'

    def handle(self, *args, **kwargs):
        os.system('pipenv run flake8 . --exclude dev.py,manage.py'
                  ',__pycache__,__init__.py,migrations --max-line-length=100')
