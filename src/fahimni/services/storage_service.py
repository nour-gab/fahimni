"""MinIO object storage helper for course files."""

import logging

import boto3

from fahimni.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """S3-compatible storage abstraction for local MinIO."""

    def __init__(self) -> None:
        self._s3 = boto3.client(
            "s3",
            endpoint_url=f"http://{settings.minio_endpoint}",
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            region_name="us-east-1",
        )

    def ensure_bucket(self) -> None:
        existing = [bucket["Name"] for bucket in self._s3.list_buckets().get("Buckets", [])]
        if settings.minio_bucket_name not in existing:
            self._s3.create_bucket(Bucket=settings.minio_bucket_name)
            logger.info("Created MinIO bucket %s", settings.minio_bucket_name)

    def upload_bytes(self, *, key: str, content: bytes, content_type: str = "application/octet-stream") -> str:
        self._s3.put_object(
            Bucket=settings.minio_bucket_name,
            Key=key,
            Body=content,
            ContentType=content_type,
        )
        return key
