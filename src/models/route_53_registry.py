import re
import boto3
from dataclasses import dataclass
from botocore.exceptions import ClientError
from returns.result import safe


@dataclass
class Route_53_registry:
    hosted_zone:str
    region:str

    def __post_init__(self):
        self.client = boto3.client('route53')
    
    @property
    def hosted_zone_id(self)->str:
        hosted_zones = self.client.list_hosted_zones_by_name()
        for zone in hosted_zones['HostedZones']:
            if zone['Name'] == self.hosted_zone + '.':
                return re.sub('/.*?/','',zone['Id'])
        return None
    
    @safe(exceptions=(ClientError))
    def create_registry(self, name:str, value:str, type:str)-> None:
        changes = [{
            'Action': 'CREATE',
            'ResourceRecordSet': {
                'Name': name,
                'Type': 'A',
                'AliasTarget': {
                    'HostedZoneId': 'Z2FDTNDATAQYW2', #hosted zone for all AWS cloud front distribution,
                    'DNSName': value,
                    'EvaluateTargetHealth': False
                }
            }
        }]
        print(changes)

        self.client.change_resource_record_sets(
            HostedZoneId=self.hosted_zone_id,
            ChangeBatch={
                'Changes': changes
            }
        )