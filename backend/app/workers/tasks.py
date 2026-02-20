from app.db.session import SessionLocal
from app.models import Document, Job, JobStatus
from app.services.pipeline import PipelineService
from app.services.storage import read_file_bytes
from app.workers.celery_app import celery_app


@celery_app.task(name="pipeline.process_document")
def process_document(document_id: str, job_id: str):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return

        file_bytes = read_file_bytes(doc.file_key)

        svc = PipelineService()
        svc.run(db, document_id=document_id, job_id=job_id, file_bytes=file_bytes)
    except Exception as exc:  # noqa: BLE001
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = JobStatus.failed
            job.error_code = "STORAGE_ERROR"
            job.error_detail = str(exc)
            db.add(job)
            db.commit()
    finally:
        db.close()
