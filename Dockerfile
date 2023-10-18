FROM python:3.9-slim as builder

RUN mkdir /app
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV TZ="Europe/Moscow"

RUN apt-get update && \
   apt-get install -y --no-install-recommends wkhtmltopdf && \
   apt-get clean && rm -rf /var/lib/apt/lists/*


COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --ignore-installed -r requirements.txt

COPY . /app/
