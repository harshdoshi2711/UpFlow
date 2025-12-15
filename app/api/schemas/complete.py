# app/api/schemas/complete.py

from pydantic import BaseModel
from uuid import UUID


class UploadCompleteResponse(BaseModel):
    upload_id: UUID
    status: str
