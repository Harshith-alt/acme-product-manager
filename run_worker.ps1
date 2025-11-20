$env:PYTHONPATH = $PWD
.\venv\Scripts\celery -A app.tasks.celery_app worker --pool=solo --loglevel=info