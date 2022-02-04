import os
from dotenv import load_dotenv

load_dotenv()

redis_host = os.getenv('REDIS_HOST')
redis_port = os.getenv('REDIS_POST')
redis_db_broker = os.getenv('REDIS_DB_CELERY_BROKER')
redis_db_result = os.getenv('REDIS_DB_CELERY_RESULT')

broker_url     = "redis://%s:%s/%s" % (redis_host, redis_port, redis_db_broker)
result_backend = "redis://%s:%s/%s" % (redis_host, redis_port, redis_db_result)

imports = {
    'celery_app.consumer'
}