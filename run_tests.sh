#!/bin/bash
pipenv run ./manage.py test -v 2 --noinput "$@"
