# syntax=docker/dockerfile:1.4
FROM python:3.10-alpine

USER root

WORKDIR /app

COPY requirements.txt /app

RUN python3 -m pip install -r requirements.txt