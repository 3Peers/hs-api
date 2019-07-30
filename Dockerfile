FROM python:3.7-stretch

ARG LOGS_DIR

RUN /bin/bash -c 'mkdir -p "$LOGS_DIR" && touch "$LOGS_DIR/debug.log"'

ADD . /opt/api
WORKDIR /opt/api

# install dependencies
RUN pip install -U pip &&\
    pip install -U pipenv &&\
    pipenv install

# start background celery worker
# TODO: find a way to substitute `LOGS_DIR`
CMD pipenv run celery -l info\
    -f "/var/log/hs-api/celery.log" -A api worker -D &&\
    pipenv run ./manage.py runserver 0:8000
