# app/api/schemas/upload.py

from pydantic import BaseModel
from uuid import UUID
from typing import List


class UploadInitRequest(BaseModel):
    filename: str
    total_chunks: int
    chunk_size: int


class UploadInitResponse(BaseModel):
    upload_id: UUID
    status: str


class UploadStatusResponse(BaseModel):
    upload_id: UUID
    filename: str
    total_chunks: int
    uploaded_chunks: List[int]
    status: str
