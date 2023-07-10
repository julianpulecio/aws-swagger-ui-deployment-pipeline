import boto3
from dataclasses import dataclass
from returns.result import safe
from botocore.exceptions import ClientError


@dataclass
class SSL_certificate:
    hosted_zone:str = None
    arn:str = None

    def __post_init__(self) -> None:
        self.client = boto3.client('acm', region_name='us-east-1')

    @safe(exceptions=(ClientError, ValueError))
    def get_certificate_from_hosted_zone(self) -> None:
        response = self.client.list_certificates()
        certificates = [
            cert for cert in response['CertificateSummaryList']
            if cert['DomainName'] == self.hosted_zone
        ]
        for cert in certificates:
            self.arn = cert['CertificateArn']
        if not self.arn:
            raise ValueError(
                f'an ACM certificate registry "{self.hosted_zone}" could not be found'
            )