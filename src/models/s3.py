import boto3
from dataclasses import dataclass


@dataclass
class S3:
    client: boto3.client = None

    def __init__(self):
        self.client = boto3.client('s3')