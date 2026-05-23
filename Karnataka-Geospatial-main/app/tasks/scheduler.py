from apscheduler.schedulers.background import BackgroundScheduler

from app.services.ingestion_service import ingest_geojson
from app.utils.logger import logger


scheduler = BackgroundScheduler()


def start_scheduler():

    logger.info(
        "Starting scheduler"
    )

    scheduler.add_job(
        ingest_geojson,
        trigger="interval",
        days=1
    )

    scheduler.start()

    logger.info(
        "Daily ingestion job scheduled"
    )