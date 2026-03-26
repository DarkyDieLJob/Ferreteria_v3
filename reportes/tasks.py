from datetime import date, datetime
import logging
from celery import shared_task

from .usecases_db import get_last_completed_week, generate_weekly_snapshot

logger = logging.getLogger('reportes')


@shared_task
def generate_current_week_snapshot_task():
    week_start, week_end = get_last_completed_week(date.today())
    created = generate_weekly_snapshot(week_start, week_end)
    logger.info(f"Weekly snapshot generated for {week_start}..{week_end}. Rows: {created}")
    return created


@shared_task
def sunday_morning_guard_task():
    # Fallback: si es domingo y no existe snapshot para la semana cerrada, generarlo
    today = date.today()
    if today.weekday() != 6:
        return 0
    week_start, week_end = get_last_completed_week(today)
    from .models import WeeklySalesSnapshot
    exists = WeeklySalesSnapshot.objects.filter(week_start=week_start, week_end=week_end).exists()
    if not exists:
        created = generate_weekly_snapshot(week_start, week_end)
        logger.info(f"Fallback Sunday snapshot generated for {week_start}..{week_end}. Rows: {created}")
        return created
    return 0
