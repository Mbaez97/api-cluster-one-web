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
  && apt-get install -y libpq-dev \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /

RUN pip install -r /requirements.txt

COPY . /app
WORKDIR /app
COPY ./compose/celery/worker/start ./start-celeryworker
RUN sed -i 's/\r//' ./start-celeryworker
RUN chmod +x ./start-celeryworker

COPY ./compose/celery/beat/start ./start-celerybeat
RUN sed -i 's/\r//' ./start-celerybeat
RUN chmod +x ./start-celerybeat

COPY ./compose/celery/flower/start ./start-flower
RUN sed -i 's/\r//' ./start-flower
RUN chmod +x ./start-flower
WORKDIR /app
