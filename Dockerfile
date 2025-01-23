FROM python:3.10

WORKDIR /app
ENV PYTHONPATH=/app

COPY ["./.env", "./group_structure.txt", "./requirements.txt", "./"]
COPY /core /app/core

RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt
