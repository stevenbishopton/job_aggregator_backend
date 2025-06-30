from datetime import datetime, timedelta, timezone
from app.db.database import SessionLocal
from app.db.models import Job
from celery import shared_task

@shared_task
def delete_old_jobs():
    session = SessionLocal()
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(weeks=2)
        deleted_count = session.query(Job).filter(Job.publication_date < cutoff_date).delete()
        session.commit()
        print(f"🗑️ Deleted {deleted_count} jobs older than 2 weeks.")
    except Exception as e:
        session.rollback()
        print(f"❌ Error deleting old jobs: {e}")
    finally:
        session.close()
