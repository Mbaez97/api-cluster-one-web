from celery import Celery  # type: ignore

from config import settings

celery_app = Celery(
    __name__, broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.task_routes = {
    "app.taskapp.tasks.test_celery": "main-queue",
}
