# app/workers/assemble.py

import tempfile
import os

from app.workers.celery_app import celery_app
from app.core.s3 import get_s3_client
from app.core.config import settings
from app.db.database import SessionLocal
from app.models.upload_session import UploadSession


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3})
def assemble_upload(self, upload_id: str):
    db = SessionLocal()
    s3 = get_s3_client()

    try:
        session = (
            db.query(UploadSession)
            .filter(UploadSession.upload_id == upload_id)
            .first()
        )

        if not session:
            raise ValueError("Upload session not found")

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            temp_path = tmp.name

            # Download chunks in order and write sequentially
            for idx in range(session.total_chunks):
                key = f"uploads/{upload_id}/chunks/{idx}"
                obj = s3.get_object(
                    Bucket=settings.AWS_S3_BUCKET,
                    Key=key,
                )
                tmp.write(obj["Body"].read())

        final_key = f"uploads/{upload_id}/final/{session.filename}"

        # Upload assembled file
        with open(temp_path, "rb") as f:
            s3.upload_fileobj(
                f,
                Bucket=settings.AWS_S3_BUCKET,
                Key=final_key,
            )

        # Cleanup chunks
        for idx in range(session.total_chunks):
            s3.delete_object(
                Bucket=settings.AWS_S3_BUCKET,
                Key=f"uploads/{upload_id}/chunks/{idx}",
            )

        session.final_s3_key = final_key
        session.status = "completed"
        db.commit()

    finally:
        db.close()
        if "temp_path" in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
