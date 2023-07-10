import os
import boto3
from returns.result import Success
from returns.pipeline import flow, is_successful
from returns.pointfree import bind
from src.helpers.find_value_by_key import find_value_by_key
from src.models.s3_bucket import S3_bucket
from src.models.s3_object import S3_object
from src.models.s3_swagger_ui_bucket import S3_swagger_ui_bucket
from src.models.ssl_certificate import SSL_certificate
from src.models.cloud_front_distribution import Cloud_front_distribution
from src.models.route_53_registry import Route_53_registry


def deploy_swagger_ui(event, context):
    result = flow(
        event,
        get_s3_content,
        bind(upload_swager_ui_s3_object),
        bind(create_cloud_front_distribution)
    )
    print(result)
    if is_successful(result):
        response = {'status_code':200, 'body':result.unwrap()}
    else:
        response = {'status_code':500, 'body':str(result.failure())}
    return response


def create_cloud_front_distribution(swagger_ui_bucket:S3_swagger_ui_bucket):
    ssl_certificate = SSL_certificate(
        hosted_zone=os.environ['ROUTE_53_HOSTED_ZONE']
    )
    cloud_front_distribution = Cloud_front_distribution(
        swagger_ui_bucket=swagger_ui_bucket,
        ssl_certificate=ssl_certificate
    )
    route_53 = Route_53_registry(
        hosted_zone=os.environ['ROUTE_53_HOSTED_ZONE'],
        region=os.environ['USER_AWS_REGION']
    )
    result = flow(
        ssl_certificate.get_certificate_from_hosted_zone(),
        bind(lambda _:cloud_front_distribution.create_distribution()),
        bind(lambda _:cloud_front_distribution.distribution_exist()),
        bind(lambda _:route_53.create_registry(
            name=swagger_ui_bucket.name,
            value=cloud_front_distribution.domain_name,
            type='A'
        ))
    )
    return result
    

def upload_swager_ui_s3_object(swagger_ui_content:dict):
    title = find_value_by_key(swagger_ui_content, 'title')

    swagger_ui_bucket = S3_swagger_ui_bucket(
        name=title,
        swagger_ui_content=swagger_ui_content,
        hosted_zone=os.environ['ROUTE_53_HOSTED_ZONE'],
        region=os.environ['USER_AWS_REGION']
    )
    result = flow(
        swagger_ui_bucket.set_name(),
        bind(lambda _:swagger_ui_bucket.validate()),
        bind(lambda _:swagger_ui_bucket.create_bucket()),
        bind(lambda _:swagger_ui_bucket.exists()),
        bind(lambda _:swagger_ui_bucket.enable_static_website_hosting()),
        bind(lambda _:swagger_ui_bucket.set_bucket_acl()),
        bind(lambda _:swagger_ui_bucket.set_bucket_policy()),
        bind(lambda _:swagger_ui_bucket.upload_content()),
        bind(lambda _:Success(swagger_ui_bucket))
    )
    return result


def get_s3_content(event:dict) -> dict:
    bucket_name = find_value_by_key(event, 'name')
    key_name = find_value_by_key(event, 'key')
    s3_bucket = S3_bucket(
        name=bucket_name
    )    
    s3_object = S3_object(
        key=key_name,
        bucket=s3_bucket
    ) 
    result = flow(
        s3_bucket.validate(),
        bind(lambda _:s3_bucket.exists()),
        bind(lambda _:s3_object.validate()),
        bind(lambda _:s3_object.get_content_from_bucket()),
    )
    return result
