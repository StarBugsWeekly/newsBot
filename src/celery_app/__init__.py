from celery import Celery

newsBot = Celery('newsBot')
newsBot.config_from_object('celery_app.celeryconfig')