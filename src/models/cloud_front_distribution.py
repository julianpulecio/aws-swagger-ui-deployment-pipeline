import boto3
from time import sleep
from dataclasses import dataclass
from botocore.exceptions import ClientError
from returns.result import safe
from src.models.s3_swagger_ui_bucket import S3_swagger_ui_bucket
from src.models.ssl_certificate import SSL_certificate


@dataclass
class Cloud_front_distribution:
    swagger_ui_bucket:S3_swagger_ui_bucket
    ssl_certificate:SSL_certificate
    id:str = None
    domain_name:str = None
    value:str = None

    def __post_init__(self):
        self.client = boto3.client('cloudfront')
    
    @safe(exceptions=(ClientError))
    def distribution_exist(self)-> bool:
        response = self.client.get_distribution(
            Id=self.id
        )

    @safe(exceptions=(ClientError))
    def create_distribution(self)-> None:
        response = self.client.create_distribution(
            DistributionConfig={
                'CallerReference': self.swagger_ui_bucket.name + '-distribution' ,
                'Aliases': {
                    'Quantity': 1,
                    'Items': [
                        self.swagger_ui_bucket.name,
                    ]
                },
                'Origins': {
                    'Quantity': 1,
                    'Items': [{
                        'Id': self.swagger_ui_bucket.static_website_url,
                        'DomainName': self.swagger_ui_bucket.static_website_url,
                        'CustomOriginConfig': {
                            'HTTPPort': 80,
                            'HTTPSPort': 443,
                            'OriginProtocolPolicy': 'http-only',
                            'OriginSslProtocols': {
                                'Quantity': 1,
                                'Items': [
                                    'TLSv1.2',
                                ]
                            },
                            'OriginReadTimeout': 5,
                            'OriginKeepaliveTimeout': 5
                        },
                    }]
                },
                'DefaultCacheBehavior': {
                    'TargetOriginId': self.swagger_ui_bucket.static_website_url,
                    'ViewerProtocolPolicy': 'redirect-to-https',
                    'AllowedMethods': {
                        'Quantity': 2,
                        'Items': ['GET', 'HEAD'],
                        'CachedMethods': {
                            'Quantity': 2,
                            'Items': ['GET', 'HEAD']
                        }
                    },
                    'Compress': True,
                    'ForwardedValues': {
                        'QueryString': False,  
                        'Cookies': {
                            'Forward': 'none'  
                        },
                        'Headers': {
                            'Quantity': 0,  
                            'Items': []
                        }
                    },
                    'MinTTL': 5,
                    'DefaultTTL': 5,
                    'MaxTTL': 5
                },
                'Enabled': True,
                'Comment': f'My {self.swagger_ui_bucket.name} distribution',
                'ViewerCertificate': {
                    'ACMCertificateArn': self.ssl_certificate.arn,
                    'SSLSupportMethod': 'sni-only', 
                    'MinimumProtocolVersion': 'TLSv1.2_2019',  
                    'Certificate': '662f9938-c12d-4a13-9c7d-f8782b7ab532',
                    'CertificateSource': 'acm'  
                }
            }    
        )
        self.domain_name = response['Distribution']['DomainName']
        self.id = response['Distribution']['Id']
        waiter = self.client.get_waiter('distribution_deployed')
        waiter.wait(
            Id=self.id,
            WaiterConfig={
                'Delay': 60,
                'MaxAttempts': 9
            }
        )