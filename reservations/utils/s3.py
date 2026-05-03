import logging
from typing import IO

import boto3
from botocore.exceptions import ClientError
from django.conf import settings

logger = logging.getLogger(__name__)


class S3Client:
    """Singleton wrapper around boto3 S3 client.

    Access via the module-level ``s3`` instance — do not instantiate directly.
    """

    _instance: "S3Client | None" = None

    def __new__(cls) -> "S3Client":
        if cls._instance is None:
            instance = super().__new__(cls)
            instance._client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION,
            )
            cls._instance = instance
        return cls._instance

    def upload_fileobj(
        self,
        file_obj: IO[bytes],
        key: str,
        bucket: str | None = None,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload a file-like object and return its public URL."""
        bucket = bucket or settings.AWS_S3_BUCKET
        self._client.upload_fileobj(
            file_obj,
            bucket,
            key,
            ExtraArgs={"ContentType": content_type},
        )
        return f"https://{bucket}.s3.{settings.AWS_S3_REGION}.amazonaws.com/{key}"

    def delete_object(self, key: str, bucket: str | None = None) -> None:
        bucket = bucket or settings.AWS_S3_BUCKET
        self._client.delete_object(Bucket=bucket, Key=key)

    def generate_presigned_url(
        self, key: str, expiry: int = 3600, bucket: str | None = None
    ) -> str:
        """Return a presigned GET URL valid for ``expiry`` seconds."""
        bucket = bucket or settings.AWS_S3_BUCKET
        try:
            return self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expiry,
            )
        except ClientError as exc:
            logger.error("Failed to generate presigned URL for key=%s: %s", key, exc)
            raise


s3 = S3Client()
