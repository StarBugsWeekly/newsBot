import os
from dotenv import load_dotenv

load_dotenv()

redis_host = os.getenv('REDIS_HOST')
redis_port = os.getenv('REDIS_POST')
redis_db   = os.getenv('REDIS_DB_CELERY_RESULT')

broker_url     = "redis://%s:%s" % (redis_host, redis_port)
result_backend = "redis://%s:%s/%s" % (redis_host, redis_port, redis_db)

imports = {
    'celery_app.consumer'
}