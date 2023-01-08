FROM python:3.9-alpine

WORKDIR /code

RUN pip install --upgrade pip

COPY ./requirements.txt /src/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY . /code/

