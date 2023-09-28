"""Celery tasks."""
from datetime import datetime


from celery import shared_task


from datetime import timedelta
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger(__name__)


@shared_task()
def test_celery(word: str) -> str:
    logger.info(f"Celery task: {word}")
    return f"test task return {word}"
