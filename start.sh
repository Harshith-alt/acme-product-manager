
mkdir -p uploads

celery -A app.tasks.celery_app worker --loglevel=info --pool=gevent --concurrency=2 &

uvicorn app.main:app --host 0.0.0.0 --port $PORT