FROM python:3.7-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY api/ /app/

CMD daphne -b 0.0.0.0 -p 80 api.asgi:application