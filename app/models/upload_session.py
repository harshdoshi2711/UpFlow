import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.database import Base


class UploadSession(Base):
    __tablename__ = "upload_sessions"

    upload_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    filename = Column(String, nullable=False)

    total_chunks = Column(Integer, nullable=False)
    chunk_size = Column(Integer, nullable=False)

    uploaded_chunks = Column(JSON, nullable=False, default=list)

    status = Column(String, nullable=False)

    final_s3_key = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
