# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.10-alpine

USER root

WORKDIR /app

COPY requirements.txt /app

# RUN --mount=type=cache,target=/root/.cache/pip \
#     pip3 install -r requirements.txt

RUN python3 -m pip install -r requirements.txt

# CMD [ "flask", "--app", "index", "--host=0.0.0.0", "--debug" ]
