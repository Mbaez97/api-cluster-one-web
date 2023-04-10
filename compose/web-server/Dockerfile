FROM python:3.8-slim-buster as base
# FROM java:11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
  # El infaltable
  && apt-get install -y tcpdump

FROM base as builder

RUN apt-get install build-essential gcc python3-dev postgresql -y \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # && apt-get install -y openjdk-11-jdk \
  && apt-get -y install default-jre-headless\
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /

RUN pip install --prefix='/install' -r /requirements.txt

FROM base

COPY --from=builder /install /usr/local

COPY . /app

WORKDIR /app