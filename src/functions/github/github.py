import os
import json
import logging
import re
import redis
import requests
from dotenv import load_dotenv
from github import Github, Repository
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class github():

    github_client = None
    redis_client = None
    redis_pool   = None

    def __init__(self):
        load_dotenv()

        github_access_token = os.getenv('GITHUB_ACCESS_TOKEN')
        redis_host          = os.getenv('REDIS_HOST')
        redis_port          = os.getenv('REDIS_POST')
        redis_db            = os.getenv('REDIS_DB_CONFIG')

        self.github_client = Github(github_access_token)
        self.redis_pool    = redis.ConnectionPool(host=redis_host, port=redis_port, db=redis_db)
        self.redis_client  = redis.Redis(connection_pool=self.redis_pool)

    def get_cached_info(self, redis_key: str):
        redis_value = self.redis_client.get(redis_key)
        return json.loads(redis_value) if redis_value else False

    def get_latest_commit(self, target_repo: Repository, publish_type: str):

        latest_commit = ''

        if publish_type == 'release':
            latest_release_tag = target_repo.get_latest_release().tag_name
            latest_commit = target_repo.get_git_tree(latest_release_tag).sha
        elif publish_type == 'push':
            latest_commit = target_repo.get_commits().get_page(-1)[0].sha
        else:
            latest_commit = ''
        
        return latest_commit

    def upsert_current_commit(self, redis_key: str, current_commit: str, publish_urls: list):
        redis_value = {
            'current_commit': current_commit,
            'publish_urls': publish_urls,
            'modified_time': time.time()
        }

        self.redis_client.set(redis_key, json.dumps(redis_value))

    def get_publich_urls(self, target_repo: Repository, base_commit: str, head_commit: str, url_pattern: str, file_regex: re.Pattern, date_regex: re.Pattern):
        compare_files = target_repo.compare(base_commit, head_commit).raw_data['files']
        publish_urls = []

        for file in compare_files:
            if file['status'] != 'added':
                continue
            
            file_match = file_regex.search(file['filename'])

            if not file_match:
                continue

            date_match = date_regex.search(file['patch'])

            url = url_pattern % (date_match.group(1).replace('-', '/'), file_match.group(1)) if date_match else url_pattern % (file_match.group(1))

            if requests.get(url).status_code == 200:
                publish_urls.append(url)
            else:
                publish_urls = []
                break

        return publish_urls

    def check_publish_status(self, repo_name: str, redis_key: str, publish_type: str, url_pattern: str, file_regex: re.Pattern, date_regex: re.Pattern):
        target_repo = self.github_client.get_repo(repo_name)
        cached_info = self.get_cached_info(redis_key)
        latest_commit = self.get_latest_commit(target_repo, publish_type)
        publich_urls = []

        if not cached_info:
            self.upsert_current_commit(redis_key, latest_commit, publich_urls)
        else:
            current_commit = cached_info['current_commit']
            publich_urls = self.get_publich_urls(target_repo, current_commit, latest_commit, url_pattern, file_regex, date_regex)

            if current_commit != latest_commit:
                self.upsert_current_commit(redis_key, latest_commit, publich_urls)

        return publich_urls