from celery import Celery  # type: ignore

from config import settings

celery_app = Celery(
    __name__, broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND  # type: ignore # noqa
)


# tasks functions
@celery_app.task(name="app.taskapp.celery.test_celery")
def test_celery(word: str) -> str:
    print(f"Celery task: {word}")
    return f"test task return {word}"
