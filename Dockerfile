FROM python:3.7-stretch

ARG LOGS_DIR

RUN /bin/bash -c 'mkdir -p "$LOGS_DIR" && touch "$LOGS_DIR/debug.log"'

ADD . /opt/api
WORKDIR /opt/api

# install dependencies
RUN pip install -U pip &&\
    pip install -U pipenv &&\
    pipenv install

# start background celery worker & beat scheduler
# TODO: find a way to substitute `LOGS_DIR`
CMD pipenv run celery -l info\
    -f "/var/log/hs-api/celery.log" -A api worker -D &&\
    pipenv run celery -l info\
    -f "/var/log/hs-api/celerybeat.log" -A api beat\
    -S django_celery_beat.schedulers:DatabaseScheduler -D &&\
    pipenv run gunicorn api.wsgi -b 0.0.0.0:8000
