release: python manage.py migrate
web: gunicorn hungry_backend_api.wsgi
worker: celery -A hungry_backend_api worker