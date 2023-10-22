# pull official base image
FROM python:3.9.6-alpine

# set work directory
WORKDIR /usr/src/orders

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies and lidmagic
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev \
    && apk add -y --no-install-recommends --no-cache libmagic

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.dev.txt .
RUN pip install -r requirements.dev.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/orders/entrypoint.sh
RUN chmod +x /usr/src/orders/entrypoint.sh

# copy project
COPY . .

