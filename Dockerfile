FROM python:3.10.2-alpine

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

EXPOSE 5000

COPY . /app