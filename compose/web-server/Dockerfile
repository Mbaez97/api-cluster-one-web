# FROM python:3.8-slim-buster as base
FROM openjdk:11-jre-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
  # El infaltable
  && apt-get install -y tcpdump

FROM base as builder

RUN apt-get install build-essential gcc python3 postgresql -y \
  && apt-get install -y python3-dev \
  && apt-get install -y python3-pip \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # Install all python:3.9-slim-buster dependencies
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /

RUN pip install -r /requirements.txt

COPY . /app

WORKDIR /app
