#!/bin/bash

export PY_ENV='test'
pipenv run ./manage.py test -v 2 --noinput "$@"
