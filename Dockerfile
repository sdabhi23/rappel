FROM node:lts as ui-build

WORKDIR /app

COPY ui/package*.json /app/

RUN npm ci

COPY ui/ /app/

RUN npm run build

FROM python:3.7-buster

COPY --from=ui-build /app/build/ /ui

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY api/ /app/

CMD daphne -b 0.0.0.0 -p 80 api.asgi:application