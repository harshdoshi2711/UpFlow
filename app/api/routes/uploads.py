from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.deps import get_db
from app.models.upload_session import UploadSession
from app.api.schemas.upload import (
    UploadInitRequest,
    UploadInitResponse,
    UploadStatusResponse,
)

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/init", response_model=UploadInitResponse)
def init_upload(payload: UploadInitRequest, db: Session = Depends(get_db)):
    session = UploadSession(
        filename=payload.filename,
        total_chunks=payload.total_chunks,
        chunk_size=payload.chunk_size,
        uploaded_chunks=[],
        status="initialized",
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return UploadInitResponse(
        upload_id=session.upload_id,
        status=session.status,
    )


@router.get("/{upload_id}/status", response_model=UploadStatusResponse)
def get_upload_status(upload_id: UUID, db: Session = Depends(get_db)):
    session = (
        db.query(UploadSession)
        .filter(UploadSession.upload_id == upload_id)
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Upload not found")

    return UploadStatusResponse(
        upload_id=session.upload_id,
        filename=session.filename,
        total_chunks=session.total_chunks,
        uploaded_chunks=session.uploaded_chunks,
        status=session.status,
    )
