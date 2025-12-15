# app/api/routes/uploads.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.deps import get_db
from app.models.upload_session import UploadSession
from app.api.schemas.upload import (
    UploadInitRequest,
    UploadInitResponse,
    UploadStatusResponse,
)
from app.api.schemas.complete import UploadCompleteResponse
from app.core.s3 import upload_chunk_to_s3

from app.workers.assemble import assemble_upload


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


@router.put("/{upload_id}/chunks/{chunk_index}")
def upload_chunk(
    upload_id: UUID,
    chunk_index: int,
    file: UploadFile,
    db: Session = Depends(get_db),
):
    session = (
        db.query(UploadSession)
        .filter(UploadSession.upload_id == upload_id)
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Upload not found")

    if session.status in ("pending_assembly", "completed"):
        raise HTTPException(
            status_code=400,
            detail="Upload already finalized",
        )

    if chunk_index < 0 or chunk_index >= session.total_chunks:
        raise HTTPException(status_code=400, detail="Invalid chunk index")

    s3_key = f"uploads/{upload_id}/chunks/{chunk_index}"

    upload_chunk_to_s3(file.file, s3_key)

    if chunk_index not in session.uploaded_chunks:
        session.uploaded_chunks.append(chunk_index)

    session.status = "uploading"
    db.commit()

    return {
        "upload_id": upload_id,
        "chunk_index": chunk_index,
        "status": "uploaded",
    }


@router.post("/{upload_id}/complete", response_model=UploadCompleteResponse)
def complete_upload(upload_id: UUID, db: Session = Depends(get_db)):
    session = (
        db.query(UploadSession)
        .filter(UploadSession.upload_id == upload_id)
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Upload not found")

    # Idempotency: already completed or pending
    if session.status in ("pending_assembly", "completed"):
        return UploadCompleteResponse(
            upload_id=session.upload_id,
            status=session.status,
        )

    uploaded = sorted(session.uploaded_chunks)
    expected = list(range(session.total_chunks))

    if uploaded != expected:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Upload incomplete",
                "uploaded_chunks": uploaded,
                "expected_chunks": expected,
            },
        )

    session.status = "pending_assembly"
    db.commit()

    assemble_upload.delay(str(upload_id))

    return UploadCompleteResponse(
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
