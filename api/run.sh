service nginx restart

daphne -u nginx.sock api.asgi:application