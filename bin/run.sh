#! /bin/sh

python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py celery worker -c 4 -l INFO
python manage.py celery beat -l INFO
python manage.py run_scheduler
gunicorn --bind "[::]:8020" -w $WEB_PROCESSES --threads $WEB_THREADS -k uvicorn_worker.UvicornWorker --proxy-protocol --proxy-allow-from "*" --forwarded-allow-ips "*" entry.asgi:application
