import json
from returns.result import safe
from dataclasses import dataclass
from botocore.exceptions import ClientError
from src.models.s3 import S3
from src.models.s3_bucket import S3_bucket


@dataclass
class S3_object(S3):
    bucket: S3_bucket = None
    key: str = None

    def __post_init__(self):
        super().__init__()

    @safe(exceptions=(ValueError,))
    def validate(self) -> bool:
        if not self.key:
            raise ValueError('key cannot be empty.')
        if not self.bucket:
            raise ValueError('bucket cannot be empty.')
        return True

    @safe(exceptions=(ClientError,))
    def get_content_from_bucket(self)-> dict:
        response = self.client.get_object(
            Bucket=self.bucket.name,
            Key=self.key
        )
        return json.loads(response['Body'].read())