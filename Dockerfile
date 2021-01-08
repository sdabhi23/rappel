FROM python:3.7-buster

RUN apt update && apt install -y nginx

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY api/ /app/

COPY nginx.conf /etc/nginx/conf.d/default.conf

CMD daphne -b 0.0.0.0 -p 80 api.asgi:application