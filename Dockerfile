FROM jfloff/alpine-python:3.7

RUN /bin/bash -c 'mkdir -p "/var/log/hs-api/" && touch "/var/log/hs-api/debug.log"'

COPY ./ /root/

WORKDIR /root/

# install dependencies
RUN pip install -U pip &&\
    pip install -U pipenv &&\
    pipenv install 

# start background celery worker & beat scheduler
# TODO: find a better way of exporting env
CMD source .env.sh &&\
    pipenv run celery -l info\
    -f "/var/log/hs-api/celery.log" -A api worker -D &&\
    pipenv run celery -l info\
    -f "/var/log/hs-api/celerybeat.log" -A api beat\
    -S django_celery_beat.schedulers:DatabaseScheduler -D &&\
    pipenv run python manage.py migrate &&\
    pipenv run gunicorn api.wsgi -b 0.0.0.0:8000
