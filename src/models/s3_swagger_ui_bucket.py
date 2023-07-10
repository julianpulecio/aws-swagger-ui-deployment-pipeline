import re
import json
import textwrap
from botocore.exceptions import ClientError
from dataclasses import dataclass
from returns.result import safe
from src.models.s3_bucket import S3_bucket


@dataclass
class S3_swagger_ui_bucket(S3_bucket):
    swagger_ui_content:str = None
    hosted_zone:str = None
    region:str = None

    @safe(exceptions=(ValueError,))
    def set_name(self)-> bool:
        if not self.name:
            raise ValueError('Bucket name cannot be empty.')
        if not self.hosted_zone:
            raise ValueError('Hosted Zone be empty.')
        clean_title = re.sub('[^a-z0-9]','', self.name.lower())
        bucket_name = clean_title + '.' + self.hosted_zone
        self.name = bucket_name

    @safe(exceptions=(ClientError,))
    def create_bucket(self)-> bool:
        self.client.create_bucket(
            Bucket=self.name,
            ObjectOwnership='BucketOwnerEnforced'
        )
        return True
    
    @safe(exceptions=(ClientError,))
    def set_bucket_acl(self):
        block_public_access_config = {
            'BlockPublicAcls': False,
            'IgnorePublicAcls': False,
            'BlockPublicPolicy': False,
            'RestrictPublicBuckets': False
        }
        self.client.put_public_access_block(
            Bucket=self.name,
            PublicAccessBlockConfiguration=block_public_access_config
        )
    
    @safe(exceptions=(ClientError,))
    def enable_static_website_hosting(self):
        self.client.put_bucket_website(
            Bucket=self.name,
            WebsiteConfiguration={
                'IndexDocument': {'Suffix': 'index.html'}
            }
        )
        
    @safe(exceptions=(ClientError,))
    def set_bucket_policy(self):
        bucket_policy = {
            'Version': '2012-10-17',
            'Statement': [{
                'Sid': 'PublicReadGetObject',
                'Effect': 'Allow',
                'Principal': '*',
                'Action': [
                    's3:GetObject'
                ],
                'Resource': f'arn:aws:s3:::{self.name}/*'
            }]
        }
        self.client.put_bucket_policy(
            Bucket=self.name,
            Policy=json.dumps(bucket_policy)
        )

    @safe(exceptions=(ClientError,))
    def upload_content(self):
        self.client.put_object(
            Bucket=self.name,
            Body=self.html_content,
            Key='index.html',
            ContentType='text/html'
        )
    
    @property
    def static_website_url(self):
        return f'{self.name}.s3-website-{self.region}.amazonaws.com'
    
    @property
    def html_content(self):
        normalized_swagger_ui_content = re.sub(
            '[(True)(False)]',lambda match: match.group(0).lower(), str(self.swagger_ui_content)
        )
        html_content = f'''
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <meta
                    name="description"
                    content="SwaggerUI"
                />
                <title>SwaggerUI</title>
                <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui.css" />
            </head>
            <body>
                <div id="swagger-ui"></div>
                <script src="https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui-bundle.js" crossorigin></script>
                <script>
                    window.onload = () => {{
                    window.ui = SwaggerUIBundle({{
                        spec: {normalized_swagger_ui_content},
                        dom_id: '#swagger-ui',
                        }});
                    }};
                </script>
            </body>
        </html>'''
        html_content = textwrap.dedent(html_content)
        return html_content