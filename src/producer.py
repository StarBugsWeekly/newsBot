import os
import re
import redis
import time
import threading
from dotenv import load_dotenv
from functions.github.github import github
from celery_app import consumer

load_dotenv()

redis_host = os.getenv('REDIS_HOST')
redis_port = os.getenv('REDIS_POST')
redis_db   = os.getenv('REDIS_DB_SUBSCRIBE')

redis_pool   = redis.ConnectionPool(host=redis_host, port=redis_port, db=redis_db)
redis_client = redis.Redis(connection_pool=redis_pool)

gitops = github()

def worker():

    while True:
        weekly_publich_urls = gitops.check_publish_status(
            repo_name = 'StarBugsWeekly/StarbugsDevOnly',
            redis_key = 'weekly',
            publish_type = 'release',
            url_pattern = "https://weekly.starbugs.dev/%s/%s/",
            file_regex = re.compile(r'source/_posts/(\d+-.*)\.md'),
            date_regex = re.compile(r'\+date: (\d{4}-\d{2}-\d{2})')
        )

        for weekly_publich_url in weekly_publich_urls:
            for subscriber in redis_client.scan_iter():
                consumer.send_message.delay(subscriber.decode(), weekly_publich_url)

        recommend_publich_urls = gitops.check_publish_status(
            repo_name = 'StarBugsWeekly/recommended_article',
            redis_key = 'recommend',
            publish_type = 'push',
            url_pattern = "https://recommend.starbugs.dev/%s/",
            file_regex = re.compile(r'(posts/starbugs-weekly/\d.+/.+).md'),
            date_regex = re.compile(r'NotNeedThis')
        )

        for recommend_publich_url in recommend_publich_urls:
            for subscriber in redis_client.scan_iter():
                consumer.send_message.delay(subscriber.decode(), recommend_publich_url)

        time.sleep(600)

thread = threading.Thread(target=worker, daemon=True)

thread.start()
thread.join()