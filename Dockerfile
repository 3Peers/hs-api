FROM python:3.7-stretch

RUN mkdir -p /var/log/hs-api && touch /var/log/hs-api/debug.log

ADD . /opt/api
WORKDIR /opt/api

RUN pip install -U pip
RUN pip install -U pipenv
RUN pipenv install --deploy --system

USER root
