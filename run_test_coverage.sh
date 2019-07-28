#!/bin/bash
pipenv run ./manage.py test -v 2 --noinput\
                      --with-coverage\
                      --cover-package='user,entities,assessments,problems'\
                      --cover-branches\
                      --cover-inclusive\
                      --cover-erase "$@"
