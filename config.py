from kombu import Exchange, Queue

BROKER_URL = "redis://127.0.0.1:6379/1"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/2"

CELERY_QUEUES = (
    Queue("for_tasks", Exchange("for_tasks"), routing_key="for_tasks"),
)
# 路由
CELERY_ROUTES = {
    'tasks.taskA': {"queue": "for_tasks", "routing_key": "for_tasks"},
    'tasks.taskB': {"queue": "for_tasks", "routing_key": "for_tasks"}
}
