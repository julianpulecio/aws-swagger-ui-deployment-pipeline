import re
from botocore.exceptions import ClientError
from dataclasses import dataclass
from returns.result import safe
from src.models.s3 import S3


@dataclass
class S3_bucket(S3):
    name: str = None

    def __post_init__(self):
        super().__init__()
    
    @safe(exceptions=(ValueError,))
    def validate(self) -> bool:
        if not self.name:
            raise ValueError('Bucket name cannot be empty.')
        if not re.fullmatch('(?!^(\d{1,3}\.){3}\d{1,3}$)(^(([a-z0-9]|[a-z0-9][a-z0-9-]*[a-z0-9])\.)*([a-z0-9]|[a-z0-9][a-z0-9-]*[a-z0-9])$)', self.name):
            raise ValueError(f'Name: {self.name} must follow the regex (?!^(\d{{1,3}}\.){{3}}\d{{1,3}}$)(^(([a-z0-9]|[a-z0-9][a-z0-9-]*[a-z0-9])\.)*([a-z0-9]|[a-z0-9][a-z0-9-]*[a-z0-9])$).')
        return True

    @safe(exceptions=(ClientError,))
    def exists(self) -> bool:
        self.client.head_bucket(
            Bucket=self.name
        )
        return True