FROM python:3.7

EXPOSE 8000

ADD app/requirements* /tmp/

WORKDIR /deploy

RUN pip install --upgrade pip && pip install -r /tmp/requirements-dev.txt
