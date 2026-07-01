web: gunicorn handwriting_project.wsgi:application
worker: celery -A handwriting_project worker -l info
