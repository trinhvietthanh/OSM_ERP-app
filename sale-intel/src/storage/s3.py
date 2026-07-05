import boto3

from src.storage.base import ObjectStorage


class S3ObjectStorage(ObjectStorage):
    """MinIO / S3-compatible store. Paths are ``s3://<bucket>/<key>``."""

    def __init__(
        self,
        endpoint_url: str,
        bucket: str,
        access_key: str,
        secret_key: str,
    ) -> None:
        self._bucket = bucket
        self._client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    def put(self, key: str, content: bytes, content_type: str) -> str:
        self._client.put_object(
            Bucket=self._bucket, Key=key, Body=content, ContentType=content_type
        )
        return f"s3://{self._bucket}/{key}"

    def get(self, path: str) -> bytes:
        prefix = f"s3://{self._bucket}/"
        if not path.startswith(prefix):
            raise ValueError(f"Not an s3 path for bucket {self._bucket}: {path!r}")
        response = self._client.get_object(
            Bucket=self._bucket, Key=path.removeprefix(prefix)
        )
        return response["Body"].read()
