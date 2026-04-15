"""Celery配置"""
from celery import Celery
from config import config

# 创建Celery实例
celery = Celery(
    'llm_eval',
    broker=config.get('celery.broker_url'),
    backend=config.get('celery.result_backend'),
    include=['backend.tasks']
)

# 配置Celery
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_default_queue='llm_eval_queue'
)

if __name__ == '__main__':
    celery.start()
