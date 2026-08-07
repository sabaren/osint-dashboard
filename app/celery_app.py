"""Celery application setup and task definitions."""

import logging
from celery import Celery
from celery.schedules import crontab

from app.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery("osint_dashboard")
celery_app.conf.update(
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_timeout=settings.CELERY_TASK_TIMEOUT,
    worker_concurrency=settings.CELERY_WORKER_CONCURRENCY,
    beat_schedule={
        "cleanup-old-data": {
            "task": "app.celery_app.cleanup_old_data",
            "schedule": crontab(hour=3, minute=0),
        },
        "weekly-backup": {
            "task": "app.celery_app.weekly_backup",
            "schedule": crontab(day_of_week=0, hour=4, minute=0),
        },
    },
)


@celery_app.task(bind=True, name="app.celery_app.scan_domain")
def scan_domain(self, domain: str, recursive: bool = False):
    """Queue a full scan for a single domain."""
    from app.database import SessionLocal
    from app.models import Scan

    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.domain == domain, Scan.status.in_(["pending", "running"])).first()
        if not scan:
            scan = Scan(domain=domain, status="running")
            db.add(scan)
            db.commit()
            db.refresh(scan)
        else:
            scan.status = "running"
            db.commit()

        self.update_state(state="PROGRESS", meta={"current": 0, "total": 5, "domain": domain})

        from app.services import run_scan_for_domain

        run_scan_for_domain(scan.id, domain, recursive, db, self)
        scan.status = "completed"
        db.commit()
    except Exception as exc:
        logger.exception("Scan failed for %s", domain)
        if scan:
            scan.status = "failed"
            db.commit()
        raise self.retry(exc=exc, max_retries=1)
    finally:
        db.close()


@celery_app.task(name="app.celery_app.cleanup_old_data")
def cleanup_old_data():
    """Remove scan results older than DATA_RETENTION_DAYS."""
    from datetime import datetime, timedelta
    from app.database import SessionLocal
    from app.models import ScanResult, Scan
    from app.config import settings

    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=settings.DATA_RETENTION_DAYS)
        old_scan_ids = db.query(Scan.id).filter(Scan.updated_at < cutoff).all()
        for (scan_id,) in old_scan_ids:
            db.query(ScanResult).filter(ScanResult.scan_id == scan_id).delete()
            db.query(Scan).filter(Scan.id == scan_id).delete()
        db.commit()
        logger.info("Cleaned up %d old scans", len(old_scan_ids))
    finally:
        db.close()


@celery_app.task(name="app.celery_app.weekly_backup")
def weekly_backup():
    """Export all scan data to JSON backup."""
    import json
    import os
    from app.database import SessionLocal
    from app.models import Scan
    from app.config import settings

    db = SessionLocal()
    try:
        os.makedirs(settings.BACKUP_DIR, exist_ok=True)
        scans = db.query(Scan).all()
        data = [
            {
                "id": s.id,
                "domain": s.domain,
                "status": s.status,
                "created_at": str(s.created_at),
                "results": [
                    {"source": r.source, "target": r.target, "data_type": r.data_type, "value": r.value}
                    for r in s.results
                ],
            }
            for s in scans
        ]
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(settings.BACKUP_DIR, f"backup_{timestamp}.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        logger.info("Backup saved to %s (%d scans)", path, len(data))
    finally:
        db.close()
