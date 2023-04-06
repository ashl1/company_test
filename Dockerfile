FROM python:3.10-slim

WORKDIR /root/

COPY app/Pipfile app/Pipfile.lock /root/

RUN pip install -U pipenv \
    && pipenv install --ignore-pipfile --deploy

COPY app/ /root/
ENTRYPOINT pipenv run uvicorn --host 0.0.0.0 main:app
