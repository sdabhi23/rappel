FROM node:lts as ui-build

WORKDIR /app

COPY ui/package*.json /app/

RUN npm ci

COPY ui/ /app/

RUN npm run build

FROM python:3.7-buster

RUN apt update && apt install -y nginx

COPY --from=ui-build /app/build/ /ui

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY api/ /app/

COPY nginx.conf /etc/nginx/nginx.conf

CMD /app/run.sh