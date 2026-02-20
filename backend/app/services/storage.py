import io
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from google.cloud import storage
from google.cloud.exceptions import NotFound

from app.core.config import settings


class StorageError(Exception):
    pass


def _s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        region_name=settings.s3_region,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
    )


def _ensure_s3_bucket(client) -> None:
    try:
        client.head_bucket(Bucket=settings.s3_bucket)
    except ClientError:
        client.create_bucket(Bucket=settings.s3_bucket)


def _gcs_client() -> storage.Client:
    return storage.Client()


def _ensure_gcs_bucket(client: storage.Client) -> storage.Bucket:
    if not settings.gcs_bucket:
        raise StorageError("GCS bucket is not configured")
    bucket = client.bucket(settings.gcs_bucket)
    try:
        bucket.reload()
    except NotFound as exc:
        raise StorageError(f"GCS bucket {settings.gcs_bucket} not found") from exc
    return bucket


def upload_fileobj(fileobj: io.BytesIO, key: str) -> None:
    backend = settings.storage_backend.lower()
    if backend == "local":
        base = Path(settings.local_storage_dir)
        target = base / key
        target.parent.mkdir(parents=True, exist_ok=True)
        fileobj.seek(0)
        target.write_bytes(fileobj.read())
        return

    if backend in {"s3", "minio"}:
        client = _s3_client()
        _ensure_s3_bucket(client)
        client.upload_fileobj(fileobj, settings.s3_bucket, key)
        return

    if backend == "gcs":
        client = _gcs_client()
        bucket = _ensure_gcs_bucket(client)
        blob = bucket.blob(key)
        fileobj.seek(0)
        blob.upload_from_file(fileobj)
        return

    raise StorageError(f"Unsupported storage backend: {settings.storage_backend}")


def delete_file(key: str) -> None:
    backend = settings.storage_backend.lower()
    if backend == "local":
        target = Path(settings.local_storage_dir) / key
        if target.exists():
            target.unlink()
        return

    if backend in {"s3", "minio"}:
        client = _s3_client()
        client.delete_object(Bucket=settings.s3_bucket, Key=key)
        return

    if backend == "gcs":
        client = _gcs_client()
        bucket = _ensure_gcs_bucket(client)
        blob = bucket.blob(key)
        blob.delete()
        return

    raise StorageError(f"Unsupported storage backend: {settings.storage_backend}")


def read_file_bytes(key: str) -> bytes:
    backend = settings.storage_backend.lower()
    if backend == "local":
        base = Path(settings.local_storage_dir)
        target = base / key
        if not target.exists():
            raise StorageError(f"Local object not found: {key}")
        return target.read_bytes()

    if backend in {"s3", "minio"}:
        client = _s3_client()
        obj = client.get_object(Bucket=settings.s3_bucket, Key=key)
        return obj["Body"].read()

    if backend == "gcs":
        client = _gcs_client()
        bucket = _ensure_gcs_bucket(client)
        blob = bucket.blob(key)
        return blob.download_as_bytes()

    raise StorageError(f"Unsupported storage backend: {settings.storage_backend}")
