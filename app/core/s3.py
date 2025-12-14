# app/core/s3.py

import boto3
from app.core.config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def upload_chunk_to_s3(file_obj, key: str):
    s3 = get_s3_client()
    s3.upload_fileobj(
        file_obj,
        Bucket=settings.AWS_S3_BUCKET,
        Key=key,
    )
