FROM python:3.7-buster

RUN apt update && apt install -y nginx

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY api/ /app/

COPY nginx.conf /etc/nginx/nginx.conf

CMD ./run.sh