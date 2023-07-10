import pytest
import boto3
import json
import os
import re
from moto import mock_s3, mock_acm, mock_route53, mock_cloudfront
from dotenv import load_dotenv
from src.helpers.find_value_by_key import find_value_by_key
from src.handler import deploy_swagger_ui


load_dotenv()
class TestCreateDeploymentProcessing:
    test_event_file = 'test_s3_object_created.json'
    test_doc_file = 'test_swagger_doc.json'

    @pytest.fixture
    def s3_event(self):
        test_event = open('src/tests/tests_files_events/' + self.test_event_file)
        return json.loads(test_event.read())

    @pytest.fixture
    def swagger_docs(self):
        test_file = open('src/tests/tests_files_swagger_docs/' + self.test_doc_file)
        return test_file.read()

    @pytest.fixture
    def s3(self, s3_event, swagger_docs):
        with mock_s3():       
            bucket_name = find_value_by_key(s3_event, 'name')
            bucket_key = find_value_by_key(s3_event, 'key')
            s3 = boto3.client(
                service_name='s3'
            )
            s3.create_bucket(
                Bucket=bucket_name
            )
            s3.put_object(
                Bucket=bucket_name,
                Body=swagger_docs,
                Key=bucket_key
            )
            yield s3
        
    @pytest.fixture
    def route_53(self):
        with mock_route53():
            route_53 = boto3.client(
                service_name='route53'
            )
            route_53.create_hosted_zone(
                Name=os.environ.get('ROUTE_53_HOSTED_ZONE'),
                CallerReference=os.environ.get('ROUTE_53_HOSTED_ZONE'),
                HostedZoneConfig={
                    'Comment': 'My hosted zone',
                    'PrivateZone': False
                }
            )
            return route_53
    
    @pytest.fixture
    def acm(self):
        with mock_acm():
            acm = boto3.client(
               service_name='acm' 
            )
            acm.request_certificate(
                DomainName=os.environ.get('ROUTE_53_HOSTED_ZONE'),
                ValidationMethod='DNS',
            )
            return acm
    
    @pytest.fixture
    def cloud_front(self):
        with mock_cloudfront():
            cloud_front = boto3.client(
               service_name='cloudfront' 
            )
            return cloud_front

    def test_initial(self, s3, route_53, acm, cloud_front, s3_event):
        deploy_swagger_ui(s3_event, '')
