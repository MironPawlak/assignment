# pull official base image
FROM alpine:3.16

# set work directory
WORKDIR /usr/src/app

# install dependencies
RUN apk update
RUN apk add --no-cache musl-dev postgresql-dev wget
RUN apk add --no-cache bash
RUN apk add --no-cache python3-dev
RUN apk add --no-cache py3-pip
RUN apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/community php

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy project
COPY ../.. .

# copy entrypoint.sh
COPY ./entrypoint.sh .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]